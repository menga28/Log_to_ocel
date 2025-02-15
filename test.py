import pm4py

ocel = pm4py.read_ocel("example.ocel")

ocel_enriched = pm4py.ocel_o2o_enrichment(
    ocel, included_graphs=["object_interaction_graph"])
