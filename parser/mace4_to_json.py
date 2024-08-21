import json
from random import randint


def extract_model(full_output, max_models):
    start_index = -1
    start_marker = "interpretation("
    end_index = -1
    end_marker = "============================== end of model =========================="

    models = []

    for i in range(max_models):
        # Find the starting point
        start_index = full_output.find(start_marker, start_index + 1)

        # Find the ending point
        end_index = full_output.find(end_marker, end_index + 1)

        if start_index != -1 and end_index != -1:
            # Extract the useful part
            model = full_output[start_index:end_index].strip()
            models.append(model)
        else:
            return None

    return models


def parse_model_output(model_output, file_name, max_models):
    objects = []
    models = extract_model(model_output, max_models)

    # Parsing the relations and their corresponding values
    for k, m in enumerate(models):
        objects_info = {"shapes": [], "connections": []}
        shape_templates = []

        lines = m.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("relation("):
                relation_name, values_str = line.split(", [")
                rel = relation_name.split("(")
                relation_name = rel[1]  # Extract relation name
                if '_' in relation_name:
                    relation_name = relation_name.split('_')[1]
                ary = (rel[2]).count("_")
                if ary > 1:
                    continue
                values = values_str.strip().strip(",").strip(" ])").split(",")
                values = [int(v) for v in values]

                # Ensure there is a template for each object
                while len(shape_templates) < len(values):
                    shape_templates.append({"type": None, "coordinates": [0, 0, 0], "dimensions": {}})

                for i, value in enumerate(values):
                    if value == 1:
                        if relation_name == "torus":
                            shape_templates[i]["type"] = "torus"
                        elif relation_name == "cylinder":
                            shape_templates[i]["type"] = "cylinder"
                        elif relation_name == "box":
                            shape_templates[i]["type"] = "cuboid"
                        elif relation_name == "sphere":
                            shape_templates[i]["type"] = "sphere"
                        elif relation_name == "center":
                            shape_templates[i]["coordinates"] = [randint(0, 5), randint(0, 5), randint(0, 5)]
                        elif relation_name == "height":
                            shape_templates[i]["dimensions"]["height"] = randint(0, 5)  # Default or parsed value
                        elif relation_name == "length":
                            shape_templates[i]["dimensions"]["length"] = randint(0, 5)  # Default or parsed value
                        elif relation_name == "width":
                            shape_templates[i]["dimensions"]["width"] = randint(0, 5)  # Default or parsed value
                        elif relation_name == "radius":
                            shape_templates[i]["dimensions"]["radius"] = randint(0, 5)  # Default or parsed value

        # Filter out any incomplete shapes and add to the final shapes list
        for shape in shape_templates:
            if shape["type"] is not None:
                objects_info["shapes"].append(shape)

        save_json(objects_info, file_name + f" ({k})")
        objects.append(objects_info)
    return objects

def save_json(content, file_name):
    f = open(f"./parser/json/{file_name}.json", "w", encoding='utf-8')
    json.dump(content, f, indent=4)
    print(f"json file saved at ./parser/json/{file_name}.json")
    f.close()


if __name__ == "__main__":
    f = open("../mace4/output/There-is-a-box.out", "r")
    model_output = f.read()
    # Parse the model output
    objects = parse_model_output(model_output, "example")

    # Convert to JSON format
    for o in objects:
        json_data = json.dumps(o, indent=4)
        print(json_data)