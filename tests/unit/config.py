# Configurazione dei parametri per i test OCEL

# Nome della colonna che rappresenta l'attività (eventi)
p_activity = "activity"

# Nome della colonna che rappresenta il timestamp
p_timestamp = "timestamp"

# Liste di parametri per testare diverse combinazioni di mappature
test_configs = [
    {
        "name": "Default Mapping",
        "p_object_types": [
            "contractAddress", "sender", "input_inputName", "storageState_variableName"
        ],
        "p_additional_event_attributes": [
            "txHash", "blockNumber", "gasUsed", "input_inputName", "input_type", "input_inputValue",
            "event_eventName", "event_eventValues.0",
            "event_eventValues.1", "event_eventValues.2",
            "event_eventValues.__length__", "event_eventValues.owner",
            "event_eventValues.spender", "event_eventValues.value",
            "event_eventValues.from", "event_eventValues.to", "event_eventValues.3",
            "event_eventValues._from", "event_eventValues._toAddress",
            "event_eventValues._amount", "storageState_variableName",
            "storageState_type", "storageState_variableValue",
            "storageState_variableRawValue", "internalTx_callType", "internalTx_to",
            "internalTx_inputsCall"
        ],
        "p_additional_object_attributes": {
            "contractAddress": ["contractAddress"],
            "input_inputName": ["input__id", "input_inputName", "input_type", "input_inputValue"],
            "storageState_variableName": [
                "storageState__id", "storageState_variableName",
                "storageState_type", "storageState_variableValue", "storageState_variableRawValue"
            ]
        }
    },
    {
        "name": "Minimal Mapping",
        "p_object_types": ["contractAddress"],
        "p_additional_event_attributes": ["txHash", "blockNumber"],
        "p_additional_object_attributes": {
            "contractAddress": ["contractAddress"]
        }
    },
    {
        "name": "Extended Mapping",
        "p_object_types": [
            "contractAddress", "sender", "input_inputName", "storageState_variableName", "internalTx_callType"
        ],
        "p_additional_event_attributes": [
            "txHash", "blockNumber", "gasUsed", "internalTx_callType", "internalTx_to", "internalTx_inputsCall"
        ],
        "p_additional_object_attributes": {
            "contractAddress": ["contractAddress"],
            "sender": ["sender"],
            "input_inputName": ["input__id", "input_inputName", "input_type", "input_inputValue"],
            "storageState_variableName": [
                "storageState__id", "storageState_variableName",
                "storageState_type", "storageState_variableValue", "storageState_variableRawValue"
            ],
            "internalTx_callType": ["internalTx_callType", "internalTx_to", "internalTx_inputsCall"]
        }
    }
]
