##This document implements the QSA off policy iteration
import numpy as np
# from tools import kronecker
import time
import matplotlib.pyplot as plt

#Helper functions:
def kronecker(A,B,n,m):

    k=A.shape[0]
    s=(int(1/2*((k)*(k+1))),1)
    C=np.ones(s)

    for i in range(n):
        C[i]=A[i]*B[i]

    for i in range(n+m-1):
        for j in range(i,n+m-1):
            C[i+n]=A[i]*B[j]

    for i in range(1,m+1):
        C[-i]=A[-i]*B[-i]

    return C

def diff_Si(U, n, m):
    s = 0.5*(len(U)*(len(U)+1))
    s = np.int(s)
    d = np.zeros(s)

    for i in range(n):
        d[i] = 2*U[i]

    for i in range(n + m - 1):
        for j in range(i, n + m - 1):
            d[i + n] = U[i] + U[j]

    for i in range(1, m + 1):
        d[-i] = 2*U[-i]

    return d

def diff_d(x,u,M,R):
    diff_d = 2*np.matmul(M,x) + 2* np.matmul(R,u)
    return diff_d

def cost_func(x,u,M,R):
    cost = np.matmul(x.T,np.matmul(M,x)) + np.matmul(u.T,np.matmul(R,u))
    return cost

def Q_func(d, Si, theta):
    Q = d + np.matmul(theta.T, Si)

    return Q

def eps_func(Q, Qscore, c, zeta, b, a, theta, M, R, x, phi, n, m):
    dQscore = diff_d(x, phi ,M,R) + np.matmul(theta.T,diff_Si(np.concatenate(x,phi), m, n)) + np.matmul(diff_theta(zeta, b, a, theta),kronecker(np.concatenate(x,phi), np.concatenate(x,phi), m, n))
    eps = -Q + Qscore + c + dQscore

    return eps

def diff_theta(zeta, b, a, theta):
    dtheta_pt1 = (np.matmul(zeta.T, theta) + b)
    dtheta = -a * np.matmul(dtheta_pt1, zeta)
    return dtheta

def compute_u(Ke, x, t):
    q = 24 #Choosen in the paper as number of sinusoids
    zeta_t = 0
    freq = np.random.choice(np.linspace(0,50),q)
    phase = np.random.choice(np.linspace(0,50),q)
    a = np.random.rand(q,1)
    for i in range(q):
        zeta_t += a[i]*np.sin(freq[i]*t + phase[i])

    u = np.matmul(Ke,x) + zeta_t

    return u

# # Start the simulation time (we can look for better place)
# start = time.time()
# t = np.copy(start)
# #Define initial states and inputs
# x = np.array([0, 0])
# u = compute_u(Ke, x, t)
#
# U = np.concatenate(x, u)
#
# n = np.size(x)  #Sates size
# m = np.size(u)  #Input size
# #Define c(x,u):
#
# c = cost_func(x,u,M,R)
# d = cost_func(x,u,M,R)
#
# #Define Si: #kronecker(A,B,n,m)
# Si = kronecker(U, U, m, n)
#
# #Define phi: = K*x
# phi = np.matmul(K,x)
#
# #Define optimization parameter, Q-functions
# theta = np.zeros(np.size(Si))
# dtheta = np.ones(np.size(Si))
# Q = Q_func(x, u, theta, M, R, m, n)
# Qscore = #Q_func(x, phi, theta, M, R, m, n)
#
# #Eq 21:
# Eps = eps_func(Q, Qscore, c, zeta, b, a, theta, M, R, x, phi, n, m)
#
# #Eq 22:
# phi = np.argmin(Q, axis = 1)
#
# #Eq 23:
# Q = d + np.matmul(theta.T,Si)
#
# #Define eq 24:
# #Define zeta:
# U1 = np.concatenate(x,phi)
# zeta_pt1 = kronecker(U1, U1, n, m)
# zeta_pt3 = diff_Si(U1, n, m)
# zeta = zeta_pt1 - Si + zeta_pt3
#
# #Define b(t):
# c = np.matmul(x.T,np.matmul(M,x)) + np.matmul(u.T,np.matmul(R,u))
# d = np.copy(c)
# dphi = np.matmul(x.T,np.matmul(M,x)) + np.matmul(phi.T,np.matmul(R,phi))
# b = c - d + dphi + diff_d(x,phi,M,R)
#
# t = time.time() - start
# a = g/(t+1)
# dtheta = theta_func(zeta, b, a, theta)

#####============STRUCTURE OF CODE==============
""""
1. Initialize all variables outside
2. While loop till theta - dtheta converges
3. counter of N = N + 1
"""

#Initialize
##Define known case for testing
A = np.array([[0, -1],[0, -0.1]])
B = np.array([0,1])
M = np.eye(2)
R = 10*np.eye(1)

g = 1.5  #Authors experimented with different values

N = 0  #Defines number of iterations

#Initialize K #In paper page 5, K = [5, 1]
K = np.array([-1, 0])
Ke = np.array([-1, -2])

#Initialize states, input and parameters
# Start the simulation time (we can look for better place)
start = time.time()
t = np.copy(start)
#Define initial states and inputs
x = np.array([0.0, 0.0])
u = compute_u(Ke, x, t)

U = np.concatenate((x, u), axis=0)

n = np.size(x)  #Sates size
m = np.size(u)  #Input size

phi = np.matmul(K,x)
phi = np.atleast_1d(phi)

size_theta = np.size(kronecker(U, U, m, n))   #Just used for gettin size for theta

theta = np.zeros(size_theta)
dtheta = np.ones(size_theta)

theta_record = []
phi_record = []
time_record = []

theta_record.append(theta)
time_record.append(t)
tol = 1e-3

###---Start the loop here:
while (np.linalg.norm(dtheta)> tol):

    # dtheta = np.copy(theta)
    N += 1

    c = cost_func(x,u,M,R)
    d = cost_func(x,u,M,R)
    U1 = np.concatenate((x,u))  # U with u
    U2 = np.concatenate((x,phi))  # U with phi
    Si = kronecker(U1, U1, m, n)

    # Implement eq 23 first:
    Q = Q_func(d, Si, theta)

    #Implement eq 24:

    #Define zeta:
    zeta_pt1 = kronecker(U2, U2, m, n)
    zeta_pt2 = kronecker(U1, U1, m, n)
    zeta_pt3 = diff_Si(U2, m, n)
    # zeta_pt3 = np.atleast_1d(zeta_pt3)
    print("part 1: ", np.shape(zeta_pt1))
    print("part 2: ", np.shape(zeta_pt2))
    print("part 3: ", np.shape(zeta_pt3))
    zeta = zeta_pt1 - zeta_pt2 + zeta_pt3

    #Define b(t):
    dphi = cost_func(x,phi,M,R)
    b = c - d + dphi + diff_d(x,phi,M,R)

    t = time.time() - start
    a = g/(t+1)
    print(np.shape(zeta))
    print(np.shape(theta))
    dtheta = diff_theta(zeta, b, a, theta)


    #Update theta
    theta = theta + dtheta
    theta_record.append(theta)

    #Implement eq 22:

    phi = np.argmin(Q, axis = 1)
    phi_record.append(phi)
    time_record.append(t)

    u = compute_u(Ke, x, t)
    x = np.matmul(A, x) + np.matmul(B, u)

print("N:",N)
##====End of while loop

#Plot functions:
plt.plot(theta_record, t)
plt.title("Plot of theta")
plt.xlabel("time (t)")
plt.ylabel("theta")
plt.show()
