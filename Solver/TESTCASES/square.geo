Point(1) = {0.0, 0.0, 0, .03};
Point(2) = {1, 0.0, 0, .03};
Point(3) = {1, 1, 0, .03};
Point(4) = {0, 1, 0, .03};
Line(1) = {4, 3};
Line(2) = {3, 2};
Line(3) = {2, 1};
Line(4) = {1, 4};
Line Loop(5) = {2, 3, 4, 1};
Plane Surface(6) = {5};
Physical Line("Border") = {1, 2, 3, 4};
Physical Surface("Inside") = {6};
Transfinite Line {1, 2, 4, 3} = 2 Using Progression 1;
Transfinite Surface {6};
