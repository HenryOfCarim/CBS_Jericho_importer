meta:
  endian: le
  file-extension: sm3
  id: sm3
  ks-version: 0.10
  title: Clive Baker's Jericho mesh format
  
seq:
  - {id: magic, contents: [0x53, 0x4d, 0x33, 0x00]}
  - {id: unk_01, type: u4}
  - {id: unk_bytes, type: u1, repeat: expr, repeat-expr: 4}
  - {id: unk_float, type: f4, repeat: expr, repeat-expr: 2}
  - {id: unk_str, type: str, size: 4, encoding: UTF-8} # SCN
  - {id: unk_int, type: u4, repeat: expr, repeat-expr: 3}
  - {id: unk_str01, type: strings_00}
  - {id: unk_int01, type: u4}  
  - {id: unk_str02, type: str, size: 4, encoding: UTF-8} # INI
  - {id: data, type: u4, repeat: expr, repeat-expr: 3}
  - {id: paths, type: strings_00, repeat: expr, repeat-expr: data[2]}
  - {id: unk_floats, type: f4, repeat: expr, repeat-expr: 15}
  - {id: num_mat, type: u4}
  - {id: materials, type: material, repeat: expr, repeat-expr: num_mat}
  - {id: unk_02, type: u4}
  - {id: num_nodes, type: u4}
  - {id: nodes, type: node, repeat: expr, repeat-expr: num_nodes}

types:
  unk_node:
    seq:
      - {id: is_exist, type: u4}
      - {id: node_id, type: u4}
  node:
    seq:
      - {id: parent_id, type: s4}
      - {id: node_id, type: s4}
      - {id: data, type: s4, repeat: expr, repeat-expr: 4}
      - {id: name_bone, type: strings_00}
      - {id: name_parent, type: strings_00}
      - {id: unk_floats, type: f4, repeat: expr, repeat-expr: 8}
      - {id: matrix, type: f4, repeat: expr, repeat-expr: 16}
      - {id: unk_floats01, type: f4, repeat: expr, repeat-expr: 23}
      - {id: is_ini_node, type: u4}
      - {id: ini, type: ini_block, repeat: expr, repeat-expr: is_ini_node}
      - {id: is_sub_node, type: u4}
      - {id: sub_node_id, type: u4, repeat: expr, repeat-expr: is_sub_node}
      - {id: mesh, type: meshes, if sub_node_id[0] == 2701131778}
      - {id: camera, type: cam, if sub_node_id[0] == 2717908996}
  meshes:
    seq:
      - {id: mesh_data, type: md3d, repeat: until, repeat-until: _.one_more == 0}
  md3d:
    seq:
       - {id: id_name, type: str, size: 4, encoding: UTF-8}
       - {id: unk_00, type: u4, repeat: expr, repeat-expr: 2}
       - {id: faces, type: face_data}
       - {id: vertices, type: vtx_data}
       - {id: num_groups, type: u4}
       - {id: unk_01, type: u4}
       - {id: groups, type: u2, repeat: expr, repeat-expr: num_groups}
       - {id: unk_02, type: u4, repeat: expr, repeat-expr: 2}
       - {id: unk_03, type: u4, repeat: expr, repeat-expr: 2}
       - {id: unk_04, type: u4, repeat: expr, repeat-expr: 2}
       - {id: unk_05, type: u4, repeat: expr, repeat-expr: 2}
       - {id: data_limited_gr, type: u4, repeat: expr, repeat-expr: 2}
       - {id: grupy, type: limited_group, if: data_limited_gr[1] == 0}
       - {id: data2, type: u4, repeat: expr, repeat-expr: 2}
       - {id: unk_struct, type: u1, repeat: expr, repeat-expr: data2[0]}
       - {id: mat_id, type: u4, repeat: expr, repeat-expr: 2}
       - {id: unk_06, type: u4}
       - {id: matrix, type: f4, repeat: expr, repeat-expr: 16}
       - {id: one_more, type: u4}
  cam:
    seq:
      - {id: node_id, type: str, size: 4, encoding: UTF-8}
      - {id: unk_00, type: u4, repeat: expr, repeat-expr: 4}
      - {id: unk_01, type: f4, repeat: expr, repeat-expr: 16}
  vertex_group:
    seq:
      - {id: num_bones, type: u4}
  face_data:
    seq:
      - {id: unk_str, type: strings_00}
      - {id: num_faces, type: u4}
      - {id: unk_01, type: u4}
      - {id: indices, type: face_indices, repeat: expr, repeat-expr: num_faces}
  vtx_data:
    seq:
      - {id: id_name, type: str, size: 4, encoding: UTF-8}
      - {id: data, type: u4, repeat: expr, repeat-expr: 4}
      - {id: vtx_format, type: u4} # 48 or 80
      - {id: num_vtx, type: u4}
      - id: vetrices 
        type:
          switch-on: vtx_format
          cases:
            48: vtx48 # static mesh
            80: vtx80
        repeat: expr
        repeat-expr: num_vtx
  vtx48:
    seq:
      - {id: position, type: f4, repeat: expr, repeat-expr: 3}
      - {id: unk_00, type: f4, repeat: expr, repeat-expr: 3}
      - {id: uv_coord, type: uv}
      - {id: unk_01, type: f4, repeat: expr, repeat-expr: 4}
  vtx80:
    seq:
      - {id: position, type: f4, repeat: expr, repeat-expr: 3}
      - {id: unk_00, type: f4, repeat: expr, repeat-expr: 3}
      - {id: uv_coord, type: uv}
      - {id: unk_01, type: f4, repeat: expr, repeat-expr: 6}
      - {id: unk_02, type: f4, repeat: expr, repeat-expr: 2}
      - {id: unk_03, type: f4, repeat: expr, repeat-expr: 4}
  uv:
    seq:
      - {id: u, type: f4}
      - {id: v, type: f4}
  limited_group:
    seq:
      - {id: num_gr, type: u4}
      - {id: unk_00, type: u4}
      - {id: grupy, type: vtx_grupy, repeat: expr, repeat-expr: num_gr}
  vtx_grupy:
    seq:
      - {id: num_gr,type: u1}
      - {id: gr, type: u1, repeat: expr, repeat-expr: 3}
      - {id: weights, type: f4, repeat: expr, repeat-expr: 3}
  face_indices:
    seq:
      - {id: idx, type: u2, repeat: expr, repeat-expr: 3}
  ini_block:
    seq:
        - {id: id_name, type: str, size: 4, encoding: UTF-8}
        - {id: data, type: u4, repeat: expr, repeat-expr: 2}
        - {id: num_strings, type: u4}
        - {id: node_strings, type: strings_00, repeat: expr, repeat-expr: num_strings}
  block_texture:
    seq:
      - {id: tex_id, type: u4}
    instances:
      is_used:
        value: tex_id != 0
      body:
          type: texture
          if: is_used
  strings_00:
    seq:
      - {id: str_size, type: u4}
      - {id: string, type: str, size: str_size, encoding: UTF-8}
  material:
    seq:
      - {id: id_name, type: str, size: 4, encoding: UTF-8}
      - {id: unk_00, type: u4}
      - {id: num_textures, type: u4}
      - {id: mat_name, type: strings_00}
      - {id: unk_size, type: u4}
      - {id: unk_nothing, size: unk_size}
      - {id: nothing, size: 12}
      - {id: nothing_02, type: u4, repeat: expr, repeat-expr: 4}
      - {id: textures, type: texture, repeat: expr, repeat-expr: num_textures}
      - {id: filler_01, type: u4, repeat: expr, repeat-expr: 4}
  texture:
   seq:
    - {id: is_texture, type: u4}
    - {id: tex_data, type: tex_body, if is_texture == 1}
  tex_body:
    seq:
    - {id: id_name, type: str, size: 4, encoding: UTF-8}
    - {id: unk_ster, type: u4, repeat: expr, repeat-expr: 2}
    - {id: str_size, type: u4}
    - {id: tex_name, type: str, size: str_size, encoding: UTF-8}
    - {id: unk_int, type: u4, repeat: expr, repeat-expr: 2}
    - {id: unk_bytes, type: u1, repeat: expr, repeat-expr: 7}
    - {id: unk_floats, type: f4, repeat: expr, repeat-expr: 3}
    - {id: unk_filler, type: u4, repeat: expr, repeat-expr: 3}