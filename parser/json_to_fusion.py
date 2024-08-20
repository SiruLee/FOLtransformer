import adsk.core, adsk.fusion, adsk.cam, traceback
import json


class ShapeObject:
    def __init__(self, coords):
        self.coords = coords


class Cylinder(ShapeObject):
    def __init__(self, coords, radius, height):
        super().__init__(coords)
        self.radius = radius
        self.height = height


class Torus(ShapeObject):
    def __init__(self, coords, inner_radius, outer_radius):
        super().__init__(coords)
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius


class Cuboid(ShapeObject):
    def __init__(self, coords, length, width, height):
        super().__init__(coords)
        self.length = length
        self.width = width
        self.height = height


class Sphere(ShapeObject):
    def __init__(self, coords, radius):
        super().__init__(coords)
        self.radius = radius


class Connection:
    def __init__(self, shape1_index, shape2_index):
        self.shape1_index = shape1_index
        self.shape2_index = shape2_index


def parse_shapes_and_coords(json_data):
    fusion_object_map = {}

    # ordered list of shape objects
    fusion_shape_list = []

    objects_info_object = json.loads(json_data)

    shape_info = objects_info_object["shapes"]
    
    for shape_info in shape_info:
        coords = shape_info.get("coordinates", [0, 0, 0])
        if isinstance(coords, tuple):
            coords = list(coords)
        dimensions = shape_info.get("dimensions", {})
        shape_type = shape_info["type"]
        
        if shape_type == "cylinder":
            shape = Cylinder(coords, dimensions.get("radius", 1), dimensions.get("height", 1))

        elif shape_type == "torus":
            shape = Torus(coords, dimensions.get("inner_radius", 1), dimensions.get("outer_radius", 1))

        elif shape_type == "cuboid":
            shape = Cuboid(coords, dimensions.get("length", 1), dimensions.get("width", 1), dimensions.get("height", 1))

        elif shape_type == "sphere":
            shape = Sphere(coords, dimensions.get("radius", 1))
            
        else:
            raise ValueError("invalid type: " + shape_type)
        
        fusion_shape_list.append(shape)

    fusion_object_map["shapes"] = fusion_shape_list

    connection_info = objects_info_object["connections"]
    
    fusion_connection_list = []

    for connection in connection_info:
        shape1_index, shape2_index = connection["shape1_index"], connection["shape2_index"]

        if shape1_index >= len(fusion_shape_list) or shape2_index >= len(fusion_shape_list):
            raise ValueError("Shape connection index out of range")
        
        conn = Connection(connection["shape1_index"], connection["shape2_index"])
        fusion_connection_list.append(conn)

    fusion_object_map["connections"] = fusion_connection_list

    return fusion_object_map


def make_cuboid(coords, length, width, height):
    app = adsk.core.Application.get()
    ui = app.userInterface
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    root_component = design.rootComponent
    sketches = root_component.sketches
    xy_plane = root_component.xYConstructionPlane

    sketch = sketches.add(xy_plane)
    sketch.isLightBulbOn = True

    x, y, z = coords
    cuboid_base_name = "cuboid_base_" + str(len(sketches))
    sketch.name = cuboid_base_name
    
    bottom_left_base = adsk.core.Point3D.create(x, y, z)
    top_right_base = adsk.core.Point3D.create(x + length, y + width, z)

    sketch.sketchCurves.sketchLines.addTwoPointRectangle(bottom_left_base, top_right_base)
    profile = root_component.sketches.itemByName(cuboid_base_name)
    cuboid_base_profile = profile.profiles.item(0)
    extrusion_extent = adsk.core.ValueInput.createByString(str(height) + " mm")
    
    root_component.features.extrudeFeatures.addSimple(cuboid_base_profile, 
                                                      extrusion_extent, 
                                                      adsk.fusion.FeatureOperations.NewBodyFeatureOperation)


def sketch_cylinder(coords, radius, height):
    app = adsk.core.Application.get()
    ui = app.userInterface
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    root_component = design.rootComponent
    sketches = root_component.sketches
    xy_plane = root_component.xYConstructionPlane

    sketch = sketches.add(xy_plane)
    cylinder_base_name = "cylinder_base_" + str(len(sketches))
    sketch.name = cylinder_base_name

    x, y, z = coords

    sketch.isLightBulbOn = True
    circle_base_center = adsk.core.Point3D.create(x, y, z)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(circle_base_center, radius)
    profile = root_component.sketches.itemByName(cylinder_base_name)

    circle_base_prof = profile.profiles.item(0)
    extrudes = root_component.features.extrudeFeatures
    extrude_input = extrudes.createInput(circle_base_prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    extrusion_distance = adsk.core.ValueInput.createByReal(height)
    extrude_input.setDistanceExtent(False, extrusion_distance)
    extrudes.add(extrude_input)


def sketch_sphere(coords, radius):
    app = adsk.core.Application.get()
    ui = app.userInterface
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    root_component = design.rootComponent
    sketches = root_component.sketches
    xy_plane = root_component.xYConstructionPlane

    sketch = sketches.add(xy_plane)
    sphere_base_name = "sphere_base_" + str(len(sketches))
    sketch.name = sphere_base_name
    sketch.isLightBulbOn = True

    x, y, z = coords

    center = adsk.core.Point3D.create(x, y, z)
    radius = 1
    sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)
    # revolution line
    revolution_line_start = adsk.core.Point3D.create(x - radius, 0, 0)
    revolution_line_end = adsk.core.Point3D.create(x + radius, 0, 0)

    line = sketch.sketchCurves.sketchLines.addByTwoPoints(
        revolution_line_start, revolution_line_end)
    profile = root_component.sketches.itemByName(sphere_base_name)
    base_circle_prof = profile.profiles.item(0)
    revolution_feature = root_component.features.revolveFeatures
    new_body_op = adsk.fusion.FeatureOperations.NewBodyFeatureOperation

    revolution = revolution_feature.createInput(base_circle_prof, line, new_body_op)
    revolution.setAngleExtent(False, adsk.core.ValueInput.createByString("360 deg"))

    revolution_feature.add(revolution)


def sketch_torus(coords, inner_radius, outer_radius):
    app = adsk.core.Application.get()
    ui = app.userInterface
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    root_component = design.rootComponent
    sketches = root_component.sketches
    xy_plane = root_component.xYConstructionPlane

    sketch = sketches.add(xy_plane)
    torus_base_name = "torus_base_" + str(len(sketches))
    sketch.name = torus_base_name
    sketch.isLightBulbOn = True

    x, y, z = coords

    outer_radius_start_point = adsk.core.Point3D.create(x, y + outer_radius, z)
    torus_base = sketch.sketchCurves.sketchCircles.addByCenterRadius(
        outer_radius_start_point, inner_radius)
    yz_plane = root_component.yZConstructionPlane
    new_sketch_axis = sketches.add(yz_plane)
    circular_sketch_axis = adsk.core.Point3D.create(x, y, z)
    torus_base = new_sketch_axis.sketchCurves.sketchCircles.addByCenterRadius(circular_sketch_axis, outer_radius)

    new_sketch_axis.name = "circular_axis_" + str(len(sketches))
    new_sketch_axis.isLightBulbOn = True
    profile = root_component.sketches.itemByName(torus_base_name)
    torus_base_prof = profile.profiles.item(0)
    extrusion_path = root_component.features.createPath(torus_base, True)
    sweep_features = root_component.features.sweepFeatures

    extrusion = sweep_features.createInput(torus_base_prof, extrusion_path,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extrusion.taperAngle = adsk.core.ValueInput.createByReal(0.0)
    extrusion.twistAngle = adsk.core.ValueInput.createByReal(0.0)

    sweep_features.add(extrusion)


def connect_shapes(shape1, shape2):
    if isinstance(shape1.coords, tuple):
        shape1.coords = list(shape1.coords)
    if isinstance(shape2.coords, tuple):
        shape2.coords = list(shape2.coords)

    if isinstance(shape1, Cuboid) and isinstance(shape2, Cuboid):
        # connect the right of shape1 to the left of shape2
        shape2.coords[0] = shape1.coords[0] + shape1.length
        shape2.coords[1] = shape1.coords[1]
        shape2.coords[2] = shape1.coords[2]

    elif isinstance(shape1, Cylinder) and isinstance(shape2, Cylinder):
        # connect top of shape1 to the bottom of shape2
        shape2.coords[2] = shape1.coords[2] + shape1.height
        shape2.coords[0] = shape1.coords[0]
        shape2.coords[1] = shape1.coords[1]

    elif isinstance(shape1, Sphere) and isinstance(shape2, Sphere):
        # align centers and offset the z radius for both shapes
        shape2.coords[0] = shape1.coords[0]
        shape2.coords[1] = shape1.coords[1]
        shape2.coords[2] = shape1.coords[2] + shape1.radius + shape2.radius

    elif isinstance(shape1, Torus) and isinstance(shape2, Torus):
        # connect top of shape1 to the bottom of shape2
        shape2.coords[0] = shape1.coords[0]
        shape2.coords[1] = shape1.coords[1]
        shape2.coords[2] = shape1.coords[2] + (shape1.outer_radius + shape2.outer_radius)

    elif isinstance(shape1, Cuboid) and isinstance(shape2, Cylinder):
        # connect top of the shape1 to the bottom of shape 2
        shape2.coords[0] = shape1.coords[0] + (shape1.length / 2) - shape2.radius
        shape2.coords[1] = shape1.coords[1] + (shape1.width / 2) - shape2.radius
        shape2.coords[2] = shape1.coords[2] + shape1.height

    elif isinstance(shape1, Cylinder) and isinstance(shape2, Cuboid):
        # connect top of the shape1 to the bottom  of the shape2
        shape2.coords[0] = shape1.coords[0] - (shape2.length / 2)
        shape2.coords[1] = shape1.coords[1] - (shape2.width / 2)
        shape2.coords[2] = shape1.coords[2] + shape1.height

    elif isinstance(shape1, Cuboid) and isinstance(shape2, Sphere):
        # align centers and offset by the height and radius
        shape2.coords[0] = shape1.coords[0] + (shape1.length / 2)
        shape2.coords[1] = shape1.coords[1] + (shape1.width / 2)
        shape2.coords[2] = shape1.coords[2] + shape1.height + shape2.radius

    elif isinstance(shape1, Sphere) and isinstance(shape2, Cuboid):
        # align centers and offset by radius
        shape2.coords[0] = shape1.coords[0] - (shape2.length / 2)
        shape2.coords[1] = shape1.coords[1] - (shape2.width / 2)
        shape2.coords[2] = shape1.coords[2] - shape1.radius

    elif isinstance(shape1, Torus) and isinstance(shape2, Cuboid):
        # connnect top of shape1 to bottom of shape2
        shape2.coords[0] = shape1.coords[0] - (shape2.length / 2)
        shape2.coords[1] = shape1.coords[1] - (shape2.width / 2)
        shape2.coords[2] = shape1.coords[2] + shape1.outer_radius

    elif isinstance(shape1, Cuboid) and isinstance(shape2, Torus):
        # connect bottom of shape1 to the top of the shape2
        shape2.coords[0] = shape1.coords[0] + (shape1.length / 2) - shape2.outer_radius
        shape2.coords[1] = shape1.coords[1] + (shape1.width / 2) - shape2.outer_radius
        shape2.coords[2] = shape1.coords[2] - shape2.outer_radius

    elif isinstance(shape1, Torus) and isinstance(shape2, Sphere):
        # align the centers and offset by outer radius
        shape2.coords[0] = shape1.coords[0]
        shape2.coords[1] = shape1.coords[1]
        shape2.coords[2] = shape1.coords[2] + shape1.outer_radius + shape2.radius

    elif isinstance(shape1, Sphere) and isinstance(shape2, Torus):
        # align the centers and offset by radius & outer radius
        shape2.coords[0] = shape1.coords[0]
        shape2.coords[1] = shape1.coords[1]
        shape2.coords[2] = shape1.coords[2] - shape1.radius - shape2.outer_radius

    elif isinstance(shape1, Cylinder) and isinstance(shape2, Sphere):
        # align centers and offset by height and radius
        shape2.coords[0] = shape1.coords[0]
        shape2.coords[1] = shape1.coords[1]
        shape2.coords[2] = shape1.coords[2] + shape1.height + shape2.radius

    elif isinstance(shape1, Sphere) and isinstance(shape2, Cylinder):
        # align centers and offset by height and radius
        shape2.coords[0] = shape1.coords[0]
        shape2.coords[1] = shape1.coords[1]
        shape2.coords[2] = shape1.coords[2] - shape1.radius - shape2.height

    elif isinstance(shape1, Cylinder) and isinstance(shape2, Torus):
        # align centers and offset by height and outer radius
        shape2.coords[0] = shape1.coords[0]
        shape2.coords[1] = shape1.coords[1]
        shape2.coords[2] = shape1.coords[2] + shape1.height + shape2.outer_radius

    elif isinstance(shape1, Torus) and isinstance(shape2, Cylinder):
        # align centers and offset by height and outer radius
        shape2.coords[0] = shape1.coords[0]
        shape2.coords[1] = shape1.coords[1]
        shape2.coords[2] = shape1.coords[2] - shape1.outer_radius - shape2.height

    else:
        raise ValueError("Invalid shapes passed in")


def sketch_all(fusion_object_map):
    shapes = fusion_object_map["shapes"]
    connections = fusion_object_map["connections"]

    for connection in connections:
        shape1 = shapes[connection.shape1_index]
        shape2 = shapes[connection.shape2_index]
        connect_shapes(shape1, shape2)

    for shape in shapes:
        if isinstance(shape, Cuboid):
            make_cuboid(shape.coords, shape.length, shape.width, shape.height)

        elif isinstance(shape, Cylinder):
            sketch_cylinder(shape.coords, shape.radius, shape.height)

        elif isinstance(shape, Sphere):
            sketch_sphere(shape.coords, shape.radius)

        elif isinstance(shape, Torus):
            sketch_torus(shape.coords, shape.inner_radius, shape.outer_radius)
            
        else:
            raise ValueError("Invalid Shape Type")


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        json_data = '''
        {
            "shapes": [
                {"type": "cylinder"},
                {"type": "cuboid"}
            ],
            "connections": [
                {"shape1_index": 0, "shape2_index": 1}
            ]
        }
        '''

        fusion_object_map = parse_shapes_and_coords(json_data)

        sketch_all(fusion_object_map)

        app.activeViewport.goHome()
        app.activeViewport.fit()

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
