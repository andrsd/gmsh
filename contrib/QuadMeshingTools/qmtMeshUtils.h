// Gmsh - Copyright (C) 1997-2020 C. Geuzaine, J.-F. Remacle
//
// See the LICENSE.txt file for license information. Please report all
// issues on https://gitlab.onelab.info/gmsh/gmsh/issues.
//
// Author: Maxence Reberol

#pragma once

#include <vector>
#include <unordered_map>
#include "SPoint2.h"
#include "SPoint3.h"


class GModel;
class GFace;
class GEdge;
class MTriangle;
class MQuadrangle;
class MVertex;
class MElement;

std::vector<GFace*> model_faces(const GModel* gm);
std::vector<GEdge*> face_edges(const GFace* gf);
std::vector<GEdge*> model_edges(const GModel* gm);

bool buildVertexToVertexMap(
    const std::vector<MTriangle*>& triangles,
    std::unordered_map<MVertex*,std::vector<MVertex*> >& v2v);


struct GFaceMeshPatch {
  /* Warning: simple container for pointers, memory not managed by this struct.
   * The GFaceMeshDiff wrapper is doing some memory management for the content. */
  GFace* gf = nullptr;
  std::vector<MVertex*> bdrVertices; /* ordered boundary loop */
  std::vector<MVertex*> intVertices;
  std::vector<MElement*> elements;
};


bool buildBoundary (const std::vector<MElement*>& elements, std::vector<MVertex*>& bnd);
bool patchFromElements(GFace* gf, const std::vector<MElement*>& elements, GFaceMeshPatch& patch);
bool patchFromQuads(GFace* gf, const std::vector<MQuadrangle*>& quads, GFaceMeshPatch& patch);

void sicnQuality(const GFaceMeshPatch& patch, double& sicnMin, double& sicnAvg);

bool patchIsTopologicallyValid(const GFaceMeshPatch& patch);

bool getConnectedComponents(const std::vector<MElement*>& elements, 
    std::vector<std::vector<MElement*> >& components);

bool setVertexGFaceUV(GFace* gf, MVertex* v, double uv[2]);

MVertex* centerOfElements(const std::vector<MElement*>& elements);

bool orientElementsAccordingToBoundarySegment(MVertex* a, MVertex* b, std::vector<MElement*>& elements);

struct GFaceMeshDiff {
  GFace* gf = nullptr;
  GFaceMeshPatch before;
  GFaceMeshPatch after;
  bool done = false;
  
  /**
   * @brief Update the GFace with the new vertices/elements
   *        and remove/delete the old ones.
   *
   * @param[in] verifyPatchTopology Check if the patch after is manifold
   *
   * @return true if success
   */
  bool execute(bool verifyPatchTopology = false);

  /**
   * @brief Destructor, delete/remove the new or old components
   *        depending on the value of the variable done.
   */
  ~GFaceMeshDiff(); 
};


/**
 * @brief Store the geometry (uv + 3D) of a GFaceMeshPatch.
 *        Useful to restore the initial geometry after trying
 *        various smoothing operations that were not successful.
 */
struct PatchGeometryBackup {
  std::vector<MVertex*> vertices;
  std::vector<SPoint2> UVs;
  std::vector<SPoint3> positions;
  std::unordered_map<MVertex*,std::pair<SPoint2,SPoint3> > old;

  PatchGeometryBackup(GFaceMeshPatch& p, bool includeBoundary = false);
  bool restore();
};
