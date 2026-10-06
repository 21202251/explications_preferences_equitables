\*  *\
Minimize
OBJ: __dummy
Subject To
Contrainte_F.15_i=0: x_0_0 = 20
Contrainte_F.15_i=1: x_0_1 = 26
Contrainte_F.15_i=2: x_0_2 = 26
Contrainte_F.15_i=3: x_0_3 = 26
Contrainte_F.15_i=4: x_0_4 = 100
Contrainte_F.16_i=0: x_3_0 = 22
Contrainte_F.16_i=1: x_3_1 = 23
Contrainte_F.16_i=2: x_3_2 = 34
Contrainte_F.16_i=3: x_3_3 = 76
Contrainte_F.16_i=4: x_3_4 = 82
Contrainte_F.17_k=1,i=0: x_1_0 - x_1_1 <= 0
Contrainte_F.17_k=1,i=1: x_1_1 - x_1_2 <= 0
Contrainte_F.17_k=1,i=2: x_1_2 - x_1_3 <= 0
Contrainte_F.17_k=1,i=3: x_1_3 - x_1_4 <= 0
Contrainte_F.17_k=2,i=0: x_2_0 - x_2_1 <= 0
Contrainte_F.17_k=2,i=1: x_2_1 - x_2_2 <= 0
Contrainte_F.17_k=2,i=2: x_2_2 - x_2_3 <= 0
Contrainte_F.17_k=2,i=3: x_2_3 - x_2_4 <= 0
Contrainte_F.18_k=0,i=0: - u_0_0 + vn_0_0 - vp_0_0 - x_0_0 + x_1_0 = 0
Contrainte_F.18_k=0,i=1: - u_0_1 + vn_0_1 - vp_0_1 - x_0_1 + x_1_1 = 0
Contrainte_F.18_k=0,i=2: - u_0_2 + vn_0_2 - vp_0_2 - x_0_2 + x_1_2 = 0
Contrainte_F.18_k=0,i=3: - u_0_3 + vn_0_3 - vp_0_3 - x_0_3 + x_1_3 = 0
Contrainte_F.18_k=0,i=4: - u_0_4 + vn_0_4 - vp_0_4 - x_0_4 + x_1_4 = 0
Contrainte_F.18_k=2,i=0: - u_2_0 + vn_2_0 - vp_2_0 - x_2_0 + x_3_0 = 0
Contrainte_F.18_k=2,i=1: - u_2_1 + vn_2_1 - vp_2_1 - x_2_1 + x_3_1 = 0
Contrainte_F.18_k=2,i=2: - u_2_2 + vn_2_2 - vp_2_2 - x_2_2 + x_3_2 = 0
Contrainte_F.18_k=2,i=3: - u_2_3 + vn_2_3 - vp_2_3 - x_2_3 + x_3_3 = 0
Contrainte_F.18_k=2,i=4: - u_2_4 + vn_2_4 - vp_2_4 - x_2_4 + x_3_4 = 0
Contrainte_F.19_k=0: - vn_0_0 - vn_0_1 - vn_0_2 - vn_0_3 - vn_0_4 + vp_0_0
 + vp_0_1 + vp_0_2 + vp_0_3 + vp_0_4 = 0
Contrainte_F.19_k=2: - vn_2_0 - vn_2_1 - vn_2_2 - vn_2_3 - vn_2_4 + vp_2_0
 + vp_2_1 + vp_2_2 + vp_2_3 + vp_2_4 = 0
_dummy: __dummy = 0
Contrainte_F.20_k=0,i=0: __dummy >= 0
Contrainte_F.20_k=0,i=1: - vn_0_0 + vp_0_0 >= 0
Contrainte_F.20_k=0,i=2: - vn_0_0 - vn_0_1 + vp_0_0 + vp_0_1 >= 0
Contrainte_F.20_k=0,i=3: - vn_0_0 - vn_0_1 - vn_0_2 + vp_0_0 + vp_0_1 + vp_0_2
 >= 0
Contrainte_F.20_k=2,i=0: __dummy >= 0
Contrainte_F.20_k=2,i=1: - vn_2_0 + vp_2_0 >= 0
Contrainte_F.20_k=2,i=2: - vn_2_0 - vn_2_1 + vp_2_0 + vp_2_1 >= 0
Contrainte_F.20_k=2,i=3: - vn_2_0 - vn_2_1 - vn_2_2 + vp_2_0 + vp_2_1 + vp_2_2
 >= 0
Contrainte_F.21_k=0: 435 beta_0 - u_0_0 - u_0_1 - u_0_2 - u_0_3 - u_0_4
 - vp_0_0 - vp_0_1 - vp_0_2 - vp_0_3 - vp_0_4 >= 0
Contrainte_F.21_k=2: 435 beta_2 - u_2_0 - u_2_1 - u_2_2 - u_2_3 - u_2_4
 - vp_2_0 - vp_2_1 - vp_2_2 - vp_2_3 - vp_2_4 >= 0
Contrainte_F.22_k=1,i=0: - 2 alpha_1_0 - x_1_0 + x_2_0 = 0
Contrainte_F.22_k=1,i=1: 4 alpha_1_0 - x_1_1 + x_2_1 = 0
Contrainte_F.22_k=1,i=2: 5 alpha_1_0 - x_1_2 + x_2_2 = 0
Contrainte_F.22_k=1,i=3: - 2 alpha_1_0 - x_1_3 + x_2_3 = 0
Contrainte_F.22_k=1,i=4: alpha_1_0 - x_1_4 + x_2_4 = 0
Contrainte_F.23_k=1: alpha_1_0 = 1
Contrainte_F.24_j=0: alpha_1_0 = 1
Bounds
 __dummy = 0
 0 <= u_0_0
 0 <= u_0_1
 0 <= u_0_2
 0 <= u_0_3
 0 <= u_0_4
 0 <= u_2_0
 0 <= u_2_1
 0 <= u_2_2
 0 <= u_2_3
 0 <= u_2_4
 0 <= vn_0_0
 0 <= vn_0_1
 0 <= vn_0_2
 0 <= vn_0_3
 0 <= vn_0_4
 0 <= vn_2_0
 0 <= vn_2_1
 0 <= vn_2_2
 0 <= vn_2_3
 0 <= vn_2_4
 0 <= vp_0_0
 0 <= vp_0_1
 0 <= vp_0_2
 0 <= vp_0_3
 0 <= vp_0_4
 0 <= vp_2_0
 0 <= vp_2_1
 0 <= vp_2_2
 0 <= vp_2_3
 0 <= vp_2_4
 0 <= x_0_0
 0 <= x_0_1
 0 <= x_0_2
 0 <= x_0_3
 0 <= x_0_4
 0 <= x_1_0
 0 <= x_1_1
 0 <= x_1_2
 0 <= x_1_3
 0 <= x_1_4
 0 <= x_2_0
 0 <= x_2_1
 0 <= x_2_2
 0 <= x_2_3
 0 <= x_2_4
 0 <= x_3_0
 0 <= x_3_1
 0 <= x_3_2
 0 <= x_3_3
 0 <= x_3_4
Generals
u_0_0
u_0_1
u_0_2
u_0_3
u_0_4
u_2_0
u_2_1
u_2_2
u_2_3
u_2_4
vn_0_0
vn_0_1
vn_0_2
vn_0_3
vn_0_4
vn_2_0
vn_2_1
vn_2_2
vn_2_3
vn_2_4
vp_0_0
vp_0_1
vp_0_2
vp_0_3
vp_0_4
vp_2_0
vp_2_1
vp_2_2
vp_2_3
vp_2_4
x_0_0
x_0_1
x_0_2
x_0_3
x_0_4
x_1_0
x_1_1
x_1_2
x_1_3
x_1_4
x_2_0
x_2_1
x_2_2
x_2_3
x_2_4
x_3_0
x_3_1
x_3_2
x_3_3
x_3_4
Binaries
alpha_1_0
beta_0
beta_2
End
