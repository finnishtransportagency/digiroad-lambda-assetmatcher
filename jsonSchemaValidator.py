from jsonschema import Draft7Validator
from jsonschema.exceptions import best_match

crs_schema = {
    "type": "object",
    "properties": {
        "type": {
            "const": "name"
        },
        "properties": {
            "type": "object",
            "properties": {
                "name": {
                    "const": "EPSG:3067"
                },
            }
        }
    }
}

linear_geometry_schema = {
    "type": "object",
    "properties": {
        "type": {
            "const": "LineString"
        },
        "coordinates": {
            "type": "array",
            "items": {
                "type": "array",
                "items": {
                    "type": "number"
                },
                "minItems": 2,
                "maxItems": 3
            },
            "uniqueItems": True,
            "minItems": 2
        },
        "crs": crs_schema
    },
    "required": ["type", "coordinates"]
}

point_geometry_schema = {
    "type": "object",
    "properties": {
        "type": {
            "const": "Point"
        },
        "coordinates": {
            "type": "array",
            "items": {
                "type": "array",
                "items": {
                    "type": "number"
                },
                "minItems": 2,
                "maxItems": 3
            },
            "minItems": 1,
            "maxItems": 1
        },
        "crs": crs_schema
    },
    "required": ["type", "coordinates"]
}

linear_properties_schema = {
    "type": "object",
    "properties": {
        "type": {
            "const": "Roadlink"
        },
        "id": {
            "type": "string",
            "minLength": 1
        },
        "name": {
            "type": "string"
        },
        "functionalClass": {
            "type": "string",
            "minLength": 1
            # Probably will be changed to receive a code value or we will invent rules to convert their string values
            # to match our functional classes
            # "enum": [1, 2, 3, 4, 5, 6, 7, 8]
        },
        "speedLimit": {
            "enum": [20, 30, 40, 50, 60, 70, 80, 90, 100, 120]
        },
        "pavementClass": {
            "enum": [1, 2, 10, 20, 30, 40, 50, 99]
        },
        "sideCode": {
            "enum": [1, 2, 3]
        }
    },
    "required": ["type", "id", "name", "functionalClass", "sideCode"],
    "minProperties": 6
}

obstacle_properties_schema = {
    "type": "object",
    "properties": {
        "type": {
            "const": "obstacle"
        },
        "id": {
            "type": "string",
            "minLength": 1
        },
        "class": {
            "enum": [1, 2]
        }
    },
    "required": ["type", "id", "class"]
}

linear_feature_schema = {
    "type": "object",
    "properties": {
        "type": {
            "const": "Feature"
        },
        "geometry": linear_geometry_schema,
        "properties": linear_properties_schema
    },
    "required": ["geometry", "properties"]
}

point_feature_schema = {
    "type": "object",
    "properties": {
        "type": {
            "const": "Feature"
        },
        "geometry": point_geometry_schema,
        "properties": {
            "anyOf": [obstacle_properties_schema]
        }
    },
    "required": ["geometry", "properties"]
}

geojson_schema = {
    "type": "object",
    "properties": {
        "type": {
            "const": "FeatureCollection"
        },
        "features": {
            "type": "array",
            "minItems": 1,
        }
    },
    "required": ["features"]
}


def validate_json(json):
    print("Beginning validation")
    validator = Draft7Validator(geojson_schema)
    error = best_match(validator.iter_errors(json))

    if error:
        return [(0, error.message)]

    features = json["features"]
    features_best_errors = []

    for feature_number, feature in enumerate(features):
        point_feature_validator = Draft7Validator(point_feature_schema)
        linear_feature_validator = Draft7Validator(linear_feature_schema)

        point_feature_error = best_match(point_feature_validator.iter_errors(feature))
        linear_feature_error = best_match(linear_feature_validator.iter_errors(feature))

        if point_feature_error and linear_feature_error:
            features_best_errors.append(
                (feature_number + 1, "If the intent was a point feature then " + point_feature_error.message +
                 ".   If the intent was a linear feature then " + linear_feature_error.message))

    if not features_best_errors:
        print("Validation Successful")

    return features_best_errors
