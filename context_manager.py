from datetime import datetime
from typing import Dict, List, Optional, Any
import json

class ContextManager:
    def __init__(self):
        self.entities = {}
        self._id_counters = {
            "dataset": 0,
            "fact": 0,
            "ctx": 0,
            "req": 0,
            "script": 0,
            "result": 0,
            "res": 0,
            "conv": 0
        }
    
    def generate_id(self, node_type):
        self._id_counters[node_type] += 1
        return f"{node_type}_{self._id_counters[node_type]:03d}"
    
    def _get_required_attributes(self, node_type):
        required_attrs = {
            "dataset": {
                "name": None,
                "description": None,
                "source": None,
                "population": None,  # renamed from rows
                "columns": None,
                "attributes": {},
                "linked_entities": {}
            },
            "fact": {
                "statement": None,
                "confidence": None,
                "source_dataset": None,
                "type": None,
                "linked_entities": {}
            },
            "ctx": {
                "title": None,
                "description": None,
                "type": None,
                "relevance_score": None,
                "confidence": None,
                "linked_entities": {}
            },
            "req": {
                "query": None,
                "timestamp": None,
                "user_id": None,
                "request_type": None,
                "linked_entities": {}
            },
            "script": {
                "name": None,
                "description": None,
                "language": None,
                "script_type": None,
                "triggered_by_request": None,
                "code": None,  # the actual script code
                "linked_entities": {}
            },
            "result": {
                "name": None,
                "description": None,
                "generated_by_script": None,
                "triggered_by_request": None,
                "result_type": None,
                "linked_entities": {}
            },
            "res": {  # response
                "response_to_request": None,
                "timestamp": None,
                "response_type": None,
                "content": None,
                "linked_entities": {}
            },
            "conv": {
                "header": None,
                "timestamp": None,
                "main_topic": None,
                "request_id": None,
                "response_id": None,
                "linked_entities": {}
            }
        }
        return required_attrs.get(node_type, {})
    
    def create_entity(self, node_type, data):
        node_id = self.generate_id(node_type)
        
        entity = {
            "node_id": node_id,
            "node_type": node_type,
            "created_timestamp": datetime.now().isoformat()
        }
        
        required_attrs = self._get_required_attributes(node_type)
        entity.update(required_attrs)
        
        entity.update(data)
        
        if "linked_entities" not in entity:
            entity["linked_entities"] = {}
        
        self.entities[node_id] = entity
        return node_id
    
    def read_entity(self, node_id):
        return self.entities.get(node_id)
    
    def update_entity(self, node_id, data):
        if node_id in self.entities:
            self.entities[node_id].update(data)
            return True
        return False
    
    def delete_entity(self, node_id):
        if node_id in self.entities:
            del self.entities[node_id]
            return True
        return False
    
    def get_entities_by_type(self, node_type):
        return {k: v for k, v in self.entities.items() if v.get("node_type") == node_type}
    
    def get_all_entities(self):
        return self.entities
    
    def link_entities(self, source_node_id, target_node_id, relationship_type="related_to"):
        if source_node_id not in self.entities:
            return False
        
        if relationship_type not in self.entities[source_node_id]["linked_entities"]:
            self.entities[source_node_id]["linked_entities"][relationship_type] = []
        
        if target_node_id not in self.entities[source_node_id]["linked_entities"][relationship_type]:
            self.entities[source_node_id]["linked_entities"][relationship_type].append(target_node_id)
        
        return True
    
    def get_linked_entities(self, node_id, relationship_type=None):
        if node_id not in self.entities:
            return {}
        
        linked = self.entities[node_id]["linked_entities"]
        
        if relationship_type:
            return linked.get(relationship_type, [])
        return linked
    
    def get_summary_view(self, node_type=None, node_id=None):
        if node_id:
            # Return summary for specific entity
            entity = self.read_entity(node_id)
            if not entity:
                return None
            return self._create_entity_summary(entity)
        
        if node_type:
            # Return summaries for all entities of this type
            entities = self.get_entities_by_type(node_type)
            return {eid: self._create_entity_summary(entity) for eid, entity in entities.items()}
        
        # Return summaries for all entities grouped by type
        summary = {}
        for etype in self._id_counters.keys():
            entities = self.get_entities_by_type(etype)
            if entities:
                summary[etype] = {eid: self._create_entity_summary(entity) for eid, entity in entities.items()}
        return summary
    
    def _create_entity_summary(self, entity):
        node_type = entity.get("node_type")
        summary = {
            "node_id": entity.get("node_id"),
            "node_type": node_type
        }
        
        if node_type == "dataset":
            summary.update({
                "name": entity.get("name"),
                "description": entity.get("description"),
                "population": entity.get("population"),
                "columns": entity.get("columns"),
                "attributes_keys": list(entity.get("attributes", {}).keys()),
                "source": entity.get("source")
            })
        elif node_type == "fact":
            summary.update({
                "statement": entity.get("statement"),
                "confidence": entity.get("confidence"),
                "type": entity.get("type"),
                "source_dataset": entity.get("source_dataset")
            })
        elif node_type == "ctx":
            summary.update({
                "title": entity.get("title"),
                "description": entity.get("description"),
                "type": entity.get("type"),
                "relevance_score": entity.get("relevance_score")
            })
        elif node_type == "req":
            summary.update({
                "query": entity.get("query"),
                "timestamp": entity.get("timestamp"),
                "request_type": entity.get("request_type"),
                "user_id": entity.get("user_id")
            })
        elif node_type == "script":
            summary.update({
                "name": entity.get("name"),
                "description": entity.get("description"),
                "language": entity.get("language"),
                "script_type": entity.get("script_type"),
                "triggered_by_request": entity.get("triggered_by_request")
            })
        elif node_type == "result":
            summary.update({
                "name": entity.get("name"),
                "description": entity.get("description"),
                "result_type": entity.get("result_type"),
                "generated_by_script": entity.get("generated_by_script")
            })
        elif node_type == "res":
            summary.update({
                "response_to_request": entity.get("response_to_request"),
                "timestamp": entity.get("timestamp"),
                "response_type": entity.get("response_type")
            })
        elif node_type == "conv":
            summary.update({
                "header": entity.get("header"),
                "timestamp": entity.get("timestamp"),
                "main_topic": entity.get("main_topic"),
                "request_id": entity.get("request_id")
            })
        
        return summary
    
    def search_entities(self, **criteria):
        results = []
        for node_id, entity in self.entities.items():
            match = True
            for key, value in criteria.items():
                if entity.get(key) != value:
                    match = False
                    break
            if match:
                results.append(node_id)
        return results
    
    def get_latest_conversation(self):
        conv_entities = self.get_entities_by_type("conv")
        if not conv_entities:
            return None
        
        latest_conv = max(conv_entities.items(), 
                         key=lambda x: x[1].get('timestamp', ''))
        return latest_conv[0]
    
    def process_request_workflow(self, request_data):
        request_id = self.create_entity("req", request_data)
        
        best_header = self.get_latest_conversation()

        conv_data = {
            "header": best_header,
            "timestamp": datetime.now().isoformat(),
            "main_topic": request_data.get("query", "")[:50] + "...",
            "request_id": request_id,
            "response_id": None
        }
        conv_id = self.create_entity("conv", conv_data)
        
        return {
            "request_id": request_id,
            "conversation_id": conv_id,
            "best_header": best_header,
            "workflow_status": "request_created"
        }
    
    def export_state(self):
        return {
            'entities': self.entities,
            'id_counters': self._id_counters
        }
    
    def import_state(self, state_data):
        self.entities = state_data.get('entities', {})
        self._id_counters = state_data.get('id_counters', {
            "dataset": 0, "fact": 0, "ctx": 0, "req": 0,
            "script": 0, "result": 0, "res": 0, "conv": 0
        })