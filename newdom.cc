 #include <iostream>
 #include <boost/graph/graphviz.hpp>
 #include <boost/graph/adjacency_list.hpp>
 #include <boost/graph/dominator_tree.hpp>
 #include <algorithm>
 #include <fstream>
 #include <cstdlib>
 #include <string>
 #include <sstream>
 #include <vector> 
 using namespace std;


 struct DominatorCorrectnessTestSet
    {
      typedef pair<int, int> edge;

      int numOfVertices;
      vector<edge> edges;
      vector<int> correctIdoms;
    };

    using namespace boost;

    typedef adjacency_list<
        listS,
        listS,
        bidirectionalS,
        property<vertex_index_t, std::size_t>, no_property> G;

    int main(int, char*[])
    {



     typedef DominatorCorrectnessTestSet::edge edge;

      DominatorCorrectnessTestSet testSet[1];



      testSet[0].numOfVertices = 8, //Orignal problem see left hand side
      testSet[0].edges.push_back(edge(0, 1));
      testSet[0].edges.push_back(edge(1, 2));
      testSet[0].edges.push_back(edge(1, 3));
      testSet[0].edges.push_back(edge(2, 7));
      testSet[0].edges.push_back(edge(3, 4));
      testSet[0].edges.push_back(edge(4, 5));
      testSet[0].edges.push_back(edge(4, 6));
      testSet[0].edges.push_back(edge(5, 7));
      testSet[0].edges.push_back(edge(6, 4));

      testSet[1].numOfVertices = 8; //Used to create Dominator Tree

    const int numOfVertices = testSet[0].numOfVertices;

    G g(
      testSet[0].edges.begin(), testSet[0].edges.end(),
      numOfVertices);

    typedef graph_traits<G>::vertex_descriptor Vertex;
    typedef property_map<G, vertex_index_t>::type IndexMap;
    typedef
      iterator_property_map<vector<Vertex>::iterator, IndexMap>
      PredMap;

    vector<Vertex> domTreePredVector, domTreePredVector2;
    IndexMap indexMap(get(vertex_index, g));
    graph_traits<G>::vertex_iterator uItr, uEnd;
    int j = 0;
    for (tie(uItr, uEnd) = vertices(g); uItr != uEnd; ++uItr, ++j)
    {
      put(indexMap, *uItr, j);
    }
    write_graphviz(cout, g);
    // Lengauer-Tarjan dominator tree algorithm
    domTreePredVector =
      vector<Vertex>(num_vertices(g), graph_traits<G>::null_vertex());
    PredMap domTreePredMap =
      make_iterator_property_map(domTreePredVector.begin(), indexMap);

    lengauer_tarjan_dominator_tree(g, vertex(0, g), domTreePredMap);
vector<int> idom(num_vertices(g));
         for (tie(uItr, uEnd) = vertices(g); uItr != uEnd; ++uItr)
         {
           if (get(domTreePredMap, *uItr) != graph_traits<G>::null_vertex())
             idom[get(indexMap, *uItr)] =
               get(indexMap, get(domTreePredMap, *uItr));
           else
             idom[get(indexMap, *uItr)] = (numeric_limits<int>::max)();
         }

        for (int k =0; k <idom.size();k++){

             if (k>0){
             cout << idom[k] << " nach " << k << endl;
             int t= idom[k];
             testSet[1].edges.push_back(edge(t, k));
             }
         }

       G g2(testSet[1].edges.begin(), testSet[1].edges.end(),8);
       int jj=0;
       for (tie(uItr, uEnd) = vertices(g2); uItr != uEnd; ++uItr, ++jj)
           {
             put(indexMap, *uItr, jj);
           }

         write_graphviz(cout, g2);
         cout << endl;


return 0;

}