// Gmsh - Copyright (C) 1997-2019 C. Geuzaine, J.-F. Remacle
//
// See the LICENSE.txt file for license information. Please report all
// issues on https://gitlab.onelab.info/gmsh/gmsh/issues.

#ifndef HIGH_ORDER_H
#define HIGH_ORDER_H

#include <vector>

class GModel;
class MElement;

void SetOrder1(GModel *m, bool onlyVisible = false);
void SetOrderN(GModel *m, int order, bool linear = true,
               bool incomplete = false, bool onlyVisible = false);
void FixPeriodicMesh(GModel *m);
void checkHighOrderTriangles(const char *cc, GModel *m,
                             std::vector<MElement *> &bad, double &minJGlob);
void checkHighOrderTetrahedron(const char *cc, GModel *m,
                               std::vector<MElement *> &bad, double &minJGlob);
void getMeshInfoForHighOrder(GModel *gm, int &meshOrder, bool &complete,
                             bool &CAD);

#endif
