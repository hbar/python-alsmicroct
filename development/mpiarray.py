import numpy as np
import logging

logger = logging.getLogger(__name__)


class MpiArray(object):
    
    # initialize array from a SINGLE source using arr\
    #    set arr and root
    # initialize array from remote sources using local_arr
    #    set local_arr and axis
    def __init__(self, arr=None, local_arr=None, axis=0, sizes=None, offsets=None, root=0, comm=None):
        # lazy load mpi4py 
        from mpi4py import MPI
        # initialize variables
        self.comm = comm or MPI.COMM_WORLD # MPI comm, used to send/recv
        self.mpi_rank = self.comm.Get_rank() # rank of this MPI process
        self.mpi_size = self.comm.Get_size() # total number of MPI processes
        self.arr = arr # full array, only stored on root mpi node
        self.local_arr = local_arr # local_arr, split along self.axis, stored on every node
        self.sizes = sizes # ndarray of sizes for local_arr
        self.offsets = offsets # ndarray of offsets for local_arr
        self.root = root # root mpi_rank that stores full arr
        self.shape = None # shape of the whole ndarray
        self.dtype = None # dtype of ndarray
        # calculate parameters for distributed array or global array
        if self.local_arr:
            #combine all shapes to get overall shape
            self.axis = axis
            total_axis_size = np.zeros(1, dtype=np.int)
            self.comm.Allreduce(np.array(data=local_arr.shape[axis], dtype=np.int), total_axis_size, op=MPI.SUM)
            self.shape = local_arr.shape[:axis]+(total_axis_size[0],)+local_arr.shape[axis:]
            self.dtype = self.local_arr.dtype
        else:
            # take size from root rank that has array (usually zero) 
            self.axis = None
            if self.arr is not None:
                shape = arr.shape
                dtype = arr.dtype
            else:
                shape = None
                dtype = None
            self.shape = self.comm.bcast(shape, root=root)
            self.dtype = self.comm.bcast(dtype, root=root)

    
    @property
    def offset(self):
        if self.offsets is None:
            return None
        else:
            return self.offsets[self.mpi_rank]

    @property
    def size(self):
        if self.sizes is None:
            return None
        else:
            return self.sizes[self.mpi_rank]

    @property
    def mpi_dtype(self):
        return self.numpy_to_mpi_dtype(self.dtype)

    @staticmethod
    def numpy_to_mpi_dtype(dtype):
        # lazy load mpi4py 
        from mpi4py import MPI        
        return MPI._typedict[dtype.char]
    
    @staticmethod
    def fromglobalarray(arr, root=0, comm=None):
        return MpiArray(arr, root=root, comm=comm)


    @staticmethod
    def fromlocalarrays(local_arr, axis=0, sizes=None, offsets=None, comm=None):
        return MpiArray(loacl_arr=local_arr, axis=axis, sizes=sizes, offsets=offsets, comm=comm)


    # scatter data to MPI nodes
    # axis determines which axis to scatter along
    # returns self.local_arr
    def scatter(self, axis=0):
        if axis not in (0,1):
            raise Exception("MpiArray can only scatter on axis 0 or 1, not %s" % str(axis))
        if self.axis is None:
            # scatter data to nodes
            # nodes calculate offsets and sizes for sharing
            self.sizes, self.offsets = self.split_array_indicies(self.shape, self.mpi_size)
            local_shape = (self.sizes[self.mpi_rank],)+self.shape[1:]
            self.local_arr = np.empty(local_shape, dtype=self.dtype)
            #TODO: compare to mpi4py Scatterv
            self._Scatterv(self.sizes, self.offsets)
            self.axis = 0 # always scatter on axis 0
        if self.axis != axis:
            # swapaxis 0 and 1 in a distributed manner
            self.swapaxes_01()
        return self.local_arr


    # replacement for the mpi4py ScatterV, which was slow for me
    # TODO: use same syntax as mpi4py
    def _Scatterv(self, sizes, offsets):
        # lazy load mpi4py 
        from mpi4py import MPI        
        # send to all nodes
        if self.mpi_rank == self.root:
            reqs = []
            for i in range(self.mpi_size):
                if i != self.root:
                    data = self.arr[offsets[i]:offsets[i]+sizes[i]]
                    reqs.append(self.comm.Isend(data, i))
            self.local_arr = self.arr[offsets[self.root]:offsets[self.root]+sizes[self.root]]
            MPI.Request.Waitall(reqs)
        else:
            self.comm.Recv(self.local_arr, source=self.root)
    
    
    # gather data from MPI nodes
    # the root mpi rank receives the actual array
    # the other MPI processes return None
    # if axis is None, data returned in current order
    # if axis == 0, data returned in original order
    # if axis == 1, data should be returned after a swapaxes (0,1) has been applied
    def gather(self, axis=0, root=0, delete_local=False):
        if axis not in (None, 0, 1):
            raise Exception("MpiArray can only gather on axis 0 or 1, not %s" % str(axis))
        elif self.axis is None:
            # array hasn't been distributed, check axis
            if self.root == root:
                # array already in correct MPI process
                if axis is None or axis == 0:
                    # array already stored correctly!
                    return self.arr
                else:
                    # array needs swapaxes, do it distributed
                    self.scatter(axis)
                    # we'll gather below
            else:
                # array not in correct MPI process
                self.scatter(axis or 0)
                self.arr = None
                # gather below
        # at this point self.axis should not be None 
        # swap axis if needed
        if axis is not None and self.axis != axis:
            self.swapaxes_01()
        # we now just need to gather the data in self.arr on the root
        if self.mpi_rank == root:
            if self.axis == 0:
                arr_shape = self.shape
            else:
                arr_shape = (self.shape[1], self.shape[0]) + self.shape[2:] 
            if self.arr is None or self.arr.shape != arr_shape:
                self.arr = np.empty(arr_shape, dtype=self.dtype)
        self._Gatherv()
        
        if delete_local:
            self.local_arr = None
            self.axis = None
        return self.arr
    
    def _Gatherv(self):
        # lazy load mpi4py 
        from mpi4py import MPI
        # all nodes send back to root
        if self.mpi_rank == self.root:
            reqs = []
            for i in range(self.mpi_size):
                if i != self.root:
                    data = self.arr[self.offsets[i]:self.offsets[i]+self.sizes[i]]
                    reqs.append(self.comm.Irecv(data, source=i))
            self.arr[self.offsets[self.root]:self.offsets[self.root]+self.sizes[self.root]] = self.local_arr[:]
            MPI.Request.Waitall(reqs)
        else:
            self.comm.Send(self.local_arr, dest=0)
        return self.arr
        

    # Do a distributed swap of axes 0 and 1
    # Equivalent to the follow, except it does it in a distributed manner
    # mpiarray.gather()
    # if mpiarray.mpi_rank == 0:
    #     np.swapaxes(mpiarray.arr, 0, 1)
    # mpiarray.scatter()
    # NOTE: must already be scattered to work.
    def swapaxes_01(self):
        if self.axis not in (0, 1):
            raise Exception("Array must already be scattered along axis 0 or 1 for swapaxes_01, not %s" % str(self.axis))
        # calculate the shape of the whole array after swapaxes
        if self.axis == 0:
            # we are switching to axis = 1
            new_shape = (self.shape[1], self.shape[0])+self.shape[2:]
        else:
            # we are switching to axis = 0
            new_shape = self.shape
        
        # planned distribution of data
        sizes, offsets = self.split_array_indicies(new_shape, self.mpi_size)
        # swap axes for sending local data and require alignment
        # NOTE: will create a copy.
        swapped_local_arr = np.require(np.swapaxes(self.local_arr, 0, 1), requirements='C')
        self.local_arr = None # no longer needed, save space
        # create flat array for recv data
        recv_stride = np.prod(new_shape[1:])
        local_arr_recv = np.empty(sizes[self.mpi_rank]*recv_stride, dtype=self.dtype)
        # calculate where to send data
        swapped_sizes, swapped_offsets = self.split_array_indicies(swapped_local_arr.shape, self.mpi_size)
        # calculate data being received in units of elements (recv is flat array)
        recv_sizes = np.empty(self.mpi_size, dtype=np.int)
        for i in range(self.mpi_size):
            recv_sizes[i] = sizes[self.mpi_rank] * self.sizes[i] * np.prod(new_shape[2:])
        recv_offsets = np.zeros(self.mpi_size, dtype=np.int)
        recv_offsets[1:] = np.cumsum(recv_sizes)[:-1]
        
        # send and receive data
        swapped_stride = np.prod(swapped_local_arr.shape[1:])
        self.comm.Alltoallv([swapped_local_arr, swapped_sizes*swapped_stride, swapped_offsets*swapped_stride, self.mpi_dtype],
                            [local_arr_recv, recv_sizes, recv_offsets, self.mpi_dtype])
        # delete sending array
        del swapped_local_arr
        # create new array to store data
        self.local_arr = np.empty((sizes[self.mpi_rank],) + new_shape[1:], dtype=self.dtype)
        # now do local copies to fix data arrangement
        for i in range(self.mpi_size):
            self.local_arr[:, self.offsets[i]:self.offsets[i]+self.sizes[i]] = local_arr_recv[recv_offsets[i]:recv_offsets[i]+recv_sizes[i]].reshape((self.local_arr.shape[0], self.sizes[i])+self.local_arr.shape[2:])
        del local_arr_recv
        self.axis ^= 1 # switched axis
        self.sizes = sizes
        self.offsets = offsets
        
        
    # Calculate offsets and indicies to split an array 
    # to send/recv from all of the MPI nodes
    @staticmethod
    def split_array_indicies(shape, mpi_size):
        # nodes calculate offsets and sizes for sharing
        chunk_size = shape[0] // mpi_size
        leftover = shape[0] % mpi_size
        sizes = np.ones(mpi_size, dtype=np.int) * chunk_size
        # evenly distribute leftover across workers
        # NOTE: currently doesn't add leftover to rank 0, 
        # since rank 0 usually has extra work to perform already
        sizes[1:leftover+1] += 1
        offsets = np.zeros(mpi_size, dtype=np.int)
        offsets[1:] = np.cumsum(sizes)[:-1]
        return sizes, offsets
