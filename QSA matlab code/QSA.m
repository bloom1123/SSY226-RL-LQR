clear all; clc; close all
addpath('Offline data generator')

load('offlinedata.mat')

%Offline data plot
plot(t,u_offline)
hold on
plot(t,x_offline)
hold off
legend("u","x_1","x_2")
title("Offline trajectory")

%Continuous system
% A = [0 -1; 0 -0.1];
% B = [0; 1];

% n = size(A,2);
[n, m] = size(B);

K = [-1 0];
% K = [-0.3357   -0.1069]; %1st value
% K = [0.1908    0.0038];   %2nd value
% K = [0.6115    0.0938];   %3rd value
% K = [1.0470    0.1973];   %4th value
% K = [-1.2286    0.5405];   %5th value
% K = [-1.2283    0.5403];   %6th value
% % K = [-1.2475    0.5297];   %7th value

K_N = zeros(size(1,n));
M = eye(n);
R = 10*eye(m);

x_init = [1, 0]';
u_init = -K*x_init;

s = 0.5*((n+m)*((n+m)+1));

theta = zeros(s,1);

dtheta = ones(s,1);
phi = 0*u_init;

g = 1;

iter = 0;

theta_record = [];
dtheta_record = [];
phi_record = [];
t_record = [];

%============Start of while loop==========================
count = 0;

for j = 1:1
while (norm(dtheta) > 1e-3)%(count<100)%
    
    iter = iter + 1;
    count = count + 1;
    
    x_off = x_offline(:,iter);
    u_off = u_offline(:,iter);
    t_off = t(:,iter);

    xdot = x_offline(:,iter+1);
%     udot = -K*xdot + GenerateNoise(t_off);
    phidot = -K*xdot;

    c_xu = cost_func(x_off,u_off, M, R);
    d_xu = cost_func(x_off,u_off, M, R);
    d_xphi = cost_func(x_off,phi, M, R);

    U1 = [x_off; u_off];
    U2 = [x_off; phi];
    Udot = [xdot; phidot];

    Si_U1 = GetKron(U1, n, m);
    Si_U2 = GetKron(U2, n, m);

    %Eq. 23:    Not used in final implementation eq. 22 used intead
    Q = Q_func(d_xu, theta, Si_U1);

    %Eq. 24:

    %Zeta(t):
    zeta(:,iter) = Si_U2 - Si_U1 + diff_Si_func(U2, Udot, n, m);

    %b(t):
    b(:,iter) = c_xu - d_xu + d_xphi + cost_diff_func(x_off, xdot, phi, phidot, M, R);

    %Theta 
    a = g/ (t_off + 1);

    dtheta  = -a * (zeta(:,iter)'*theta + b(:,iter))*zeta(:,iter);

    theta = theta + h*dtheta;
    
    %Eq. 22:
    Q_phi = GetVec2mat(theta,n , m);
    Qux = Q_phi(end,1:n);
    
    K_N = Qux;
    phi = -inv(R)*Qux*x_off;
    
    %Store theta and phi
    theta_record = [theta_record theta];
    dtheta_record = [dtheta_record dtheta];
    phi_record = [phi_record phi];
    t_record = [t_record t_off];
end
end
%============End of while loop============================
disp("Feedback gain is: ")
disp(K_N)
check_val(A, B, x_init, u_init, iter, K_N, n, m, t_record)

%Plots
figure()
% plot([1:iter-1],phi_record)
plot(t_record,phi_record)
xlabel("time")
title("Phi record")

figure()
plot(t_record,theta_record)
xlabel("time")
% plot([1:iter-1],theta_record)
title("\theta record")

figure()
plot(t_record,dtheta_record)
xlabel("time")
% plot([1:iter-1],dtheta_record)
title('$\displaystyle\frac{d\theta}{dt}$ record','interpreter','latex')