import os
import json
from typing import Optional
from models import ProcessResponse

class JobManager:
    def __init__(self):
        self.jobs_dir = "jobs_cache"
        os.makedirs(self.jobs_dir, exist_ok=True)
    
    def save(self, job: ProcessResponse):
        path = os.path.join(self.jobs_dir, f"{job.request_id}.json")
        try:
            # Pydantic v2
            data = job.model_dump_json()
        except AttributeError:
            # Pydantic v1
            data = job.json()
            
        temp_path = f"{path}.tmp"
        with open(temp_path, "w") as f:
            f.write(data)
        os.rename(temp_path, path)
            
    def get(self, request_id: str) -> Optional[ProcessResponse]:
        path = os.path.join(self.jobs_dir, f"{request_id}.json")
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = f.read()
                    try:
                        return ProcessResponse.model_validate_json(data)
                    except AttributeError:
                        return ProcessResponse.parse_raw(data)
            except Exception:
                return None
        return None

job_manager = JobManager()
