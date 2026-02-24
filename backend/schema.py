from cerberus import Validator

users_schema = {
    "browser_id":{
        'type':'string',
        'required':True
    },
    "user_name":{
        'type':'string',
        'minlength':3,
        'required':True
    },
    "phoneNo":{
        'type':'string',
        'minlength':10,
        'maxlength':12,
        'required':True
    },
    "email":{
        'type':'string',
        'required':True
    },
    "password":{
        'type':'string',
        'minlength':6,
        'required':True
    }
}

driver_schema = {
    "browser_id":{
        'type':'string',
        'required':True
    },
    "driver_name":{
        'type':  'string',
        'minlength':3,
        'required':True
    },
    "phoneNo":{
        'type':'string',
        'minlength':10,
        'maxlength':12,
        'required':True
    },
    "email":{
        'type':'string',
        'required':True
    },
    "password":{
        'type':'string',
        'minlength':6,
        'required':True
    },
    "vehicle_name":{
        'type':  'string',
        'minlength':3,
        'required':True
    },
    "VehicleNo":{
        'type':'string',
        'minlength':10,
        'maxlength':10,
        'required':True
    },
    "vehicle_type":{
        'type':'string',
        'allowed':['Bike','Auto','Car','Truck'],
        'required':True
    }
}
trip_schema = {
    "user_id": {
        "type": "string", 
        "required": True
    },
    "driver_id": {
        "type": "string", 
        "required": False, 
        "nullable": True
    },
    "vehicle_type_requested": {
        "type": "string", 
        "allowed": ['Bike', 'Auto', 'Car', 'Truck']
    },
    "source": {
    "type": "dict",
    "schema": {
        "type": {"type": "string", "default": "Point"},
        "coordinates": {
            "type": "list", 
            "schema": {"type": "float"}, 
            "minlength": 2, 
            "maxlength": 2
        }
    }
},
   "destination": {
    "type": "dict",
    "schema": {
        "type": {"type": "string", "default": "Point"},
        "coordinates": {
            "type": "list", 
            "schema": {"type": "float"}, 
            "minlength": 2, 
            "maxlength": 2
        }
    }
},

"status": {
        "type": "string",
        "default": "Requested",
        "allowed": ["Requested", "Driver_Assigned", "Ongoing", "Completed", "Cancelled"]
    },
    
"fare": {
        "type": "float", 
        "required": False,
        "nullable": True
    },
    "distance": {
        "type": "float", 
        "required": False,
        "nullable": True
    },
    "created_at": {
        "type": "string", # Changed to string to store ISO format (more common for JSON APIs)
        "required": False 
    }
}

user_validator = Validator(users_schema)
driver_validator = Validator(driver_schema)
trip_validator = Validator(trip_schema)