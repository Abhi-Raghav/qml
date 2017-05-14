# MIT License
#
# Copyright (c) 2016 Anders Steen Christensen, Felix Faber
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np
from numpy import empty, asfortranarray, ascontiguousarray, zeros

from fkernels import fgaussian_kernel
from fkernels import flaplacian_kernel
from fkernels import fget_vector_kernels_gaussian
from fkernels import fget_vector_kernels_laplacian


def laplacian_kernel(A, B, sigma):
    """ Calculates the Laplacian kernel matrix K, where K_ij:

            K_ij = exp(-1 * sigma**(-1) * || A_i - B_j ||_1)

        Where A_i and B_j are descriptor vectors.

        K is calculated using an OpenMP parallel Fortran routine.

        NOTE: A and B need not be input as Fortran contiguous arrays.

        Arguments:
        ==============
        A -- np.array of np.array of descriptors.
        B -- np.array of np.array of descriptors.
        sigma -- The value of sigma in the kernel matrix.

        Returns:
        ==============
        K -- The Laplacian kernel matrix.
    """

    na = A.shape[1]
    nb = B.shape[1]

    K = empty((na, nb), order='F')
    flaplacian_kernel(A, na, B, nb, K, sigma)

    return K


def gaussian_kernel(A, B, sigma):
    """ Calculates the Gaussian kernel matrix K, where K_ij:

            K_ij = exp(-0.5 * sigma**(-2) * || A_i - B_j ||_2)

        Where A_i and B_j are descriptor vectors.

        K is calculated using an OpenMP parallel Fortran routine.

        NOTE: A and B need not be input as Fortran contiguous arrays.

        Arguments:
        ==============
        A -- np.array of np.array of descriptors.
        B -- np.array of np.array of descriptors.
        sigma -- The value of sigma in the kernel matrix.

        Returns:
        ==============
        K -- The Gaussian kernel matrix.
    """

    na = A.shape[1]
    nb = B.shape[1]

    K = empty((na, nb), order='F')

    fgaussian_kernel(A, na, B, nb, K, sigma)

    return K


def get_atomic_kernels_laplacian(x1, x2, N1, N2, sigmas):

     nm1 = len(N1)
     nm2 = len(N2)
 
     n1 = np.array(N1,dtype=np.int32)
     n2 = np.array(N2,dtype=np.int32)
 
     nsigmas = len(sigmas)
     sigmas = np.array(sigmas)
 
     return fget_vector_kernels_laplacian(x1, x2, n1, n2, sigmas, \
         nm1, nm2, nsigmas)

     
def get_atomic_kernels_gaussian(mols1, mols2, sigmas):

    n1 = np.array([mol.natoms for mol in mols1], dtype=np.int32)
    n2 = np.array([mol.natoms for mol in mols2], dtype=np.int32)

    amax1 = np.amax(n1)
    amax2 = np.amax(n2)

    nm1 = len(mols1)
    nm2 = len(mols2)
    
    cmat_size = mols1[0].local_coulomb_matrix.shape[1]

    x1 = np.zeros((nm1,amax1,cmat_size), dtype=np.float64, order="F")
    x2 = np.zeros((nm2,amax2,cmat_size), dtype=np.float64, order="F")

    for imol in range(nm1):
        x1[imol,:n1[imol],:cmat_size] = mols1[imol].local_coulomb_matrix

    for imol in range(nm2):
        x2[imol,:n2[imol],:cmat_size] = mols2[imol].local_coulomb_matrix

    # Reorder for Fortran speed
    x1 = np.swapaxes(x1,0,2)
    x2 = np.swapaxes(x2,0,2)

    nsigmas = len(sigmas)

    sigmas = np.array(sigmas, dtype=np.float64)
    
    return fget_vector_kernels_gaussian(x1, x2, n1, n2, sigmas, \
        nm1, nm2, nsigmas)

