## 1. Update the elim_V2_paths() and elim_V1_paths() in "Seaice_step5_reverse_eliminate_V1_V2_no_threshold.ipynb"
+ if one_Co_t_ids and reversed_V2_paths:
+ sublist and sublist[0]
+ return None
Previous:
```
# a function to eliminate the involved V2-paths
def elim_V2_paths(reversed_V2_paths, one_Co_t_ids):
    if one_Co_t_ids and reversed_V2_paths: # this V2-path should be eliminated
        # for each sublist (the V2-path) in reversed_V2_paths, if its first element is not contained in one_Co_t_ids, we eliminate it
        filtered_V2_paths = list(filter(lambda sublist: sublist[0] not in one_Co_t_ids, reversed_V2_paths))
        return filtered_V2_paths
    else: # return the original V2-paths
        return reversed_V2_paths
    
elim_V2_paths_udf = udf(elim_V2_paths, ArrayType(ArrayType(IntegerType())))
```

Now (12/19/2025):
```
# a function to eliminate the involved V2-paths
def elim_V2_paths(reversed_V2_paths, one_Co_t_ids):
    if one_Co_t_ids and reversed_V2_paths: # this V2-path should be eliminated
        # for each sublist (the V2-path) in reversed_V2_paths, if its first element is not contained in one_Co_t_ids, we eliminate it
        filtered_V2_paths = list(filter(lambda sublist: sublist and sublist[0] not in one_Co_t_ids, reversed_V2_paths))
        return filtered_V2_paths
    else: # return the original V2-paths
        return None
    
elim_V2_paths_udf = udf(elim_V2_paths, ArrayType(ArrayType(IntegerType())))
```

## 2. Update collect_set() in "Seaice_step3_save_potential_simplex_pais_to_rm_no_threshold.ipynb" and "Seaice_step5_reverse_eliminate_V1_V2_no_threshold.ipynb"
+ collect_list() to collect_set()
Previous:
```
# broadcast left join connected components with saddles
saddles_per_con_ET_init = result_con_ET.join(df_crit_E_Co_tris,result_con_ET.tri==df_crit_E_Co_tris.Saddle_Co_t, "inner")

saddles_per_con_ET = saddles_per_con_ET_init.groupBy('component').agg(collect_list('Saddle_edge').alias('multi_Saddles'), collect_list('id').alias('multi_Saddles_co_tri_id'))
saddles_per_con_ET.printSchema()
```
Now:
```
# broadcast left join connected components with saddles
saddles_per_con_ET_init = result_con_ET.join(df_crit_E_Co_tris,result_con_ET.tri==df_crit_E_Co_tris.Saddle_Co_t, "inner")

saddles_per_con_ET = saddles_per_con_ET_init.groupBy('component').agg(collect_list('Saddle_edge').alias('multi_Saddles'), collect_set('id').alias('multi_Saddles_co_tri_id'))
saddles_per_con_ET.printSchema()
```

## 3. Update "Seaice_step7_resimplify_r1_step5_reverse_eliminate_V1_V2_threshold.ipynb"
+ function reverse_V2_ET() when two_Saddle_Co_t_id has a length of 1
Previous:
```
# a function to reverse the Forman gradient (V1-paths)
def reverse_V2_ET(two_Saddle_Co_t_id, V2_paths):
    if not V2_paths:
        return None
    if two_Saddle_Co_t_id:
        index_to_reverse = -1
#         for i in range(len(V2_paths)):
#             if V2_paths[i][0] in two_Saddle_Co_t_id:
#                 index_to_reverse = i
#                 # get the co-boundary triangle this saddle and this co-boundary triangle is not contained in this component
#                 if V2_paths[i][0] == two_Saddle_Co_t_id[0]:
#                     pot_saddle_unique_co_t = two_Saddle_Co_t_id[1]
#                 else:
#                     pot_saddle_unique_co_t = two_Saddle_Co_t_id[0]
#                 break
        
        sad_Co_t0_connected_with_crit_t = False
        sad_Co_t1_connected_with_crit_t = False
        for i in range(len(V2_paths)):
            if V2_paths[i] and V2_paths[i][0] in two_Saddle_Co_t_id:
                index_to_reverse = i                
                # get the co-boundary triangle this saddle and this co-boundary triangle is not contained in this component
                if V2_paths[i][0] == two_Saddle_Co_t_id[0]:
                    sad_Co_t0_connected_with_crit_t = True
                    if len(two_Saddle_Co_t_id) > 1:
                        pot_saddle_unique_co_t = two_Saddle_Co_t_id[1]
                    else:
                        pot_saddle_unique_co_t = -1
                        continue
                    
                if V2_paths[i][0] == two_Saddle_Co_t_id[1]:
                    sad_Co_t1_connected_with_crit_t = True
                    if len(two_Saddle_Co_t_id) > 1:
                        pot_saddle_unique_co_t = two_Saddle_Co_t_id[0]
                    else:
                        pot_saddle_unique_co_t = -1
                    
        
        if sad_Co_t0_connected_with_crit_t and sad_Co_t1_connected_with_crit_t:
            # both of the two extreme vertices of a saddle are connected with crit_v
            return None
                
        if index_to_reverse != -1:
           #  V2_paths[index_to_reverse].reverse()
            # concatenate the V-paths
            new_V2_paths = []
            set_reverse = set(V2_paths[index_to_reverse])
            for i in range(len(V2_paths)):
                if i != index_to_reverse and V2_paths[i]:
                    # test if part of V2_paths[index_to_reverse] is already in V2_paths[i]
                    set1 = set(V2_paths[i])
                    common_tri_id = set1.intersection(set_reverse)
                    lst1 = V2_paths[i][0:(len(V2_paths[i]) - len(common_tri_id) + 1)]
                    lst2 = V2_paths[index_to_reverse][0:(len(V2_paths[index_to_reverse]) - len(common_tri_id))]
                    lst2.reverse()
                    lst2.append(pot_saddle_unique_co_t) # add the other end point of this saddle
                    new_V2_paths.append(lst1+lst2)
                    
            return new_V2_paths
    else:
        return V2_paths

reverse_V2_ET_udf = udf(reverse_V2_ET, ArrayType(ArrayType(IntegerType())))
```
New update on 12/19/2025:
```
# a function to reverse the Forman gradient (V1-paths)
def reverse_V2_ET(two_Saddle_Co_t_id, V2_paths):
    if two_Saddle_Co_t_id:
        index_to_reverse = -1
#         for i in range(len(V2_paths)):
#             if V2_paths[i][0] in two_Saddle_Co_t_id:
#                 index_to_reverse = i
#                 # get the co-boundary triangle this saddle and this co-boundary triangle is not contained in this component
#                 if V2_paths[i][0] == two_Saddle_Co_t_id[0]:
#                     pot_saddle_unique_co_t = two_Saddle_Co_t_id[1]
#                 else:
#                     pot_saddle_unique_co_t = two_Saddle_Co_t_id[0]
#                 break
        
        sad_Co_t0_connected_with_crit_t = False
        sad_Co_t1_connected_with_crit_t = False
        pot_saddle_unique_co_t = None
        for i in range(len(V2_paths)):
            if V2_paths[i][0] in two_Saddle_Co_t_id:
                index_to_reverse = i
#                 if len(two_Saddle_Co_t_id) < 2:
#                     break
                # get the co-boundary triangle this saddle and this co-boundary triangle is not contained in this component
                if len(two_Saddle_Co_t_id) > 1 and V2_paths[i][0] == two_Saddle_Co_t_id[0]:
                    pot_saddle_unique_co_t = two_Saddle_Co_t_id[1]
                    sad_Co_t0_connected_with_crit_t = True
                if len(two_Saddle_Co_t_id) > 1 and V2_paths[i][0] == two_Saddle_Co_t_id[1]:
                    pot_saddle_unique_co_t = two_Saddle_Co_t_id[0]
                    sad_Co_t1_connected_with_crit_t = True
        
        if sad_Co_t0_connected_with_crit_t and sad_Co_t1_connected_with_crit_t:
            # both of the two extreme vertices of a saddle are connected with crit_v
            return None
                
        if index_to_reverse != -1:
           #  V2_paths[index_to_reverse].reverse()
            # concatenate the V-paths
            new_V2_paths = []
            set_reverse = set(V2_paths[index_to_reverse])
            for i in range(len(V2_paths)):
                if i != index_to_reverse:
                    # test if part of V2_paths[index_to_reverse] is already in V2_paths[i]
                    set1 = set(V2_paths[i])
                    common_tri_id = set1.intersection(set_reverse)
                    lst1 = V2_paths[i][0:(len(V2_paths[i]) - len(common_tri_id) + 1)]
                    lst2 = V2_paths[index_to_reverse][0:(len(V2_paths[index_to_reverse]) - len(common_tri_id))]
                    lst2.reverse()
                    if pot_saddle_unique_co_t:
                        lst2.append(pot_saddle_unique_co_t) # add the other end point of this saddle
                    new_V2_paths.append(lst1+lst2)
                    
            return new_V2_paths
    else:
        return V2_paths

reverse_V2_ET_udf = udf(reverse_V2_ET, ArrayType(ArrayType(IntegerType())))
```

New update on 01/15/2026:
+ remove the case of return None
+ add the special case when there is only one path in V2_paths
```
# a function to reverse the Forman gradient (V1-paths)
def reverse_V2_ET(two_Saddle_Co_t_id, V2_paths):
    if two_Saddle_Co_t_id:
        index_to_reverse = -1
#         for i in range(len(V2_paths)):
#             if V2_paths[i][0] in two_Saddle_Co_t_id:
#                 index_to_reverse = i
#                 # get the co-boundary triangle this saddle and this co-boundary triangle is not contained in this component
#                 if V2_paths[i][0] == two_Saddle_Co_t_id[0]:
#                     pot_saddle_unique_co_t = two_Saddle_Co_t_id[1]
#                 else:
#                     pot_saddle_unique_co_t = two_Saddle_Co_t_id[0]
#                 break
        
        sad_Co_t0_connected_with_crit_t = False
        sad_Co_t1_connected_with_crit_t = False
        pot_saddle_unique_co_t = None
        for i in range(len(V2_paths)):
            if V2_paths[i][0] in two_Saddle_Co_t_id:
                index_to_reverse = i
#                 if len(two_Saddle_Co_t_id) < 2:
#                     break
                # get the co-boundary triangle this saddle and this co-boundary triangle is not contained in this component
                if len(two_Saddle_Co_t_id) > 1 and V2_paths[i][0] == two_Saddle_Co_t_id[0]:
                    pot_saddle_unique_co_t = two_Saddle_Co_t_id[1]
                    sad_Co_t0_connected_with_crit_t = True
                if len(two_Saddle_Co_t_id) > 1 and V2_paths[i][0] == two_Saddle_Co_t_id[1]:
                    pot_saddle_unique_co_t = two_Saddle_Co_t_id[0]
                    sad_Co_t1_connected_with_crit_t = True
        
#         if sad_Co_t0_connected_with_crit_t and sad_Co_t1_connected_with_crit_t:
#             # both of the two extreme vertices of a saddle are connected with crit_v
#             return None
                
        if index_to_reverse != -1:
           #  V2_paths[index_to_reverse].reverse()
            # concatenate the V-paths
            new_V2_paths = []
            set_reverse = set(V2_paths[index_to_reverse])
            for i in range(len(V2_paths)):
                if i != index_to_reverse:
                    # test if part of V2_paths[index_to_reverse] is already in V2_paths[i]
                    set1 = set(V2_paths[i])
                    common_tri_id = set1.intersection(set_reverse)
                    lst1 = V2_paths[i][0:(len(V2_paths[i]) - len(common_tri_id) + 1)]
                    lst2 = V2_paths[index_to_reverse][0:(len(V2_paths[index_to_reverse]) - len(common_tri_id))]
                    lst2.reverse()
                    if pot_saddle_unique_co_t:
                        lst2.append(pot_saddle_unique_co_t) # add the other end point of this saddle
                    new_V2_paths.append(lst1+lst2)
                    
            if len(new_V2_paths) == 0: # a special case when there is only one path in V2_paths
                V2_paths_origin = V2_paths[index_to_reverse]
                V2_paths_origin.reverse()
                if pot_saddle_unique_co_t:
                    V2_paths_origin.append(pot_saddle_unique_co_t)
                    
                new_V2_paths.append(V2_paths_origin)
                
            return new_V2_paths
    else:
        return V2_paths

reverse_V2_ET_udf = udf(reverse_V2_ET, ArrayType(ArrayType(IntegerType())))
```
Update on 01/16/2026:
+ add pot_saddle_unique_co_t only when it is not None and it is not -1
```
# a function to reverse the Forman gradient (V1-paths)
def reverse_V2_ET(two_Saddle_Co_t_id, V2_paths):
    if two_Saddle_Co_t_id:
        index_to_reverse = -1
#         for i in range(len(V2_paths)):
#             if V2_paths[i][0] in two_Saddle_Co_t_id:
#                 index_to_reverse = i
#                 # get the co-boundary triangle this saddle and this co-boundary triangle is not contained in this component
#                 if V2_paths[i][0] == two_Saddle_Co_t_id[0]:
#                     pot_saddle_unique_co_t = two_Saddle_Co_t_id[1]
#                 else:
#                     pot_saddle_unique_co_t = two_Saddle_Co_t_id[0]
#                 break
        
        sad_Co_t0_connected_with_crit_t = False
        sad_Co_t1_connected_with_crit_t = False
        pot_saddle_unique_co_t = None
        for i in range(len(V2_paths)):
            if V2_paths[i][0] in two_Saddle_Co_t_id:
                index_to_reverse = i
#                 if len(two_Saddle_Co_t_id) < 2:
#                     break
                # get the co-boundary triangle this saddle and this co-boundary triangle is not contained in this component
                if len(two_Saddle_Co_t_id) > 1 and V2_paths[i][0] == two_Saddle_Co_t_id[0]:
                    pot_saddle_unique_co_t = two_Saddle_Co_t_id[1]
                    sad_Co_t0_connected_with_crit_t = True
                if len(two_Saddle_Co_t_id) > 1 and V2_paths[i][0] == two_Saddle_Co_t_id[1]:
                    pot_saddle_unique_co_t = two_Saddle_Co_t_id[0]
                    sad_Co_t1_connected_with_crit_t = True
        
#         if sad_Co_t0_connected_with_crit_t and sad_Co_t1_connected_with_crit_t:
#             # both of the two extreme vertices of a saddle are connected with crit_v
#             return None
                
        if index_to_reverse != -1:
           #  V2_paths[index_to_reverse].reverse()
            # concatenate the V-paths
            new_V2_paths = []
            set_reverse = set(V2_paths[index_to_reverse])
            for i in range(len(V2_paths)):
                if i != index_to_reverse:
                    # test if part of V2_paths[index_to_reverse] is already in V2_paths[i]
                    set1 = set(V2_paths[i])
                    common_tri_id = set1.intersection(set_reverse)
                    lst1 = V2_paths[i][0:(len(V2_paths[i]) - len(common_tri_id) + 1)]
                    lst2 = V2_paths[index_to_reverse][0:(len(V2_paths[index_to_reverse]) - len(common_tri_id))]
                    lst2.reverse()
                    if pot_saddle_unique_co_t and pot_saddle_unique_co_t != -1: # a boundary critical triangle if it is -1
                        lst2.append(pot_saddle_unique_co_t) # add the other end point of this saddle
                    new_V2_paths.append(lst1+lst2)
                    
            if len(new_V2_paths) == 0: # a special case when there is only one path in V2_paths
                V2_paths_origin = V2_paths[index_to_reverse]
                V2_paths_origin.reverse()
                if pot_saddle_unique_co_t:
                    V2_paths_origin.append(pot_saddle_unique_co_t)
                    
                new_V2_paths.append(V2_paths_origin)
                
            return new_V2_paths
    else:
        return V2_paths

reverse_V2_ET_udf = udf(reverse_V2_ET, ArrayType(ArrayType(IntegerType())))
```

## 4. Update "contract_VE()" in "Seaice_step7_resimplify_r1_step5_reverse_eliminate_V1_V2_threshold.ipynb"
Update on 01/16/2026:
+ do not simplify the minimum-saddle pair if the saddle has a elevation greater than 0.6m
```
if simplify_with_order == '1' or simplify_with_order == 'yes' or simplify_with_order == 'y':
    # check if the saddle-minima pair could be contracted
    def contract_VE(pot_saddle, pot_minimum, multi_components_VE, multi_Max_tri):
        # pot_saddle: the center saddle, which is the saddle to be contracted in the saddle-minima pair
        # pot_minimum: the critical vertex to be contracted in the saddle-minima pair
        # multi_components_VE: the other critical vertices that are connected with the pot_saddle
        # multi_Max_tri: the critical triangles that are connected with the pot_saddle
        
        if pot_saddle == None or pot_minimum == None:
            return
        
        persist_value = pot_saddle[0] - pot_minimum
#         persist_value_thre = 1000
#         if persist_value < persist_value_thre:
#             less_than_thre = True
#         else:
#             less_than_thre = False
        
        less_than_thre = True
        smallest_mini_saddle = True
        smallest_max_saddle = True
        if len(multi_components_VE) > 0:
            for crit_ver in multi_components_VE:
                if pot_saddle[0] - crit_ver < persist_value:
                # if crit_ver < pot_minimum:
                    smallest_mini_saddle = False
                    
        if len(multi_Max_tri) > 0:
            for crit_tri in multi_Max_tri:
                if crit_tri[0] - pot_saddle[0] < persist_value:
                    smallest_max_saddle = False
            
        contract = smallest_mini_saddle and smallest_max_saddle and less_than_thre
        return contract
else:
    print("Simplification according to elevation!")
    # get the elevation values of each vertex
    df_ver_order = df_ver_order.sort(col('self_order'), ascending=True)

    # collect df_ver_order as a global array 
    df_ver_order_col = df_ver_order.collect()
    # check if the saddle-minima pair could be contracted
    
    def contract_VE(pot_saddle, pot_minimum, multi_components_VE, multi_Max_tri):
        # pot_saddle: the center saddle, which is the saddle to be contracted in the saddle-minima pair
        # pot_minimum: the critical vertex to be contracted in the saddle-minima pair
        # multi_components_VE: the other critical vertices that are connected with the pot_saddle
        # multi_Max_tri: the critical triangles that are connected with the pot_saddle
        
        if pot_saddle == None or pot_minimum == None:
            return
        
        persist_value = df_ver_order_col[pot_saddle[0]]['ele'] - df_ver_order_col[pot_minimum]['ele']
        persist_value_thre = 0.25
        if persist_value < persist_value_thre:
            less_than_thre = True
        else:
            less_than_thre = False
        
    #     less_than_thre = True
        smallest_mini_saddle = True
        smallest_max_saddle = True
        if len(multi_components_VE) > 0:
            for crit_ver in multi_components_VE:
                if df_ver_order_col[pot_saddle[0]]['ele'] - df_ver_order_col[crit_ver]['ele'] < persist_value:
                # if crit_ver < pot_minimum:
                    smallest_mini_saddle = False
                    
        if len(multi_Max_tri) > 0:
            for crit_tri in multi_Max_tri:
                if df_ver_order_col[crit_tri[0]]['ele'] - df_ver_order_col[pot_saddle[0]]['ele'] < persist_value:
                    smallest_max_saddle = False
            
        saddle_smaller_than_thre = True
        if df_ver_order_col[pot_saddle[1]]['ele'] >= 0.6:
            saddle_smaller_than_thre = False
            
        contract = smallest_mini_saddle and smallest_max_saddle and saddle_smaller_than_thre and less_than_thre
        return contract
```
