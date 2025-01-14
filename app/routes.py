from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response, request
from datetime import datetime
import requests
import os
from dotenv import load_dotenv



tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    
    if request.method == "GET":
        sort_query = request.args.get("sort")
        
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())
         
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc())
            
        else:
            tasks = Task.query.all()

        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at != None  
            })

        return jsonify(tasks_response), 200


    elif request.method == "POST":
        request_body = request.get_json()
        
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:

            return jsonify({
                "details": "Invalid data"
            }), 400

        new_task = Task(title=request_body["title"], description=request_body["description"],
        completed_at=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit()
       
        return jsonify(
            {
                "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": new_task.completed_at != None  
                }
            }), 201

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response(f"Task {task_id} not found", 404)

    if request.method == "GET":
        if task.goal_id:
            return {
            "task": {
                "id": task.task_id,
                "goal_id": task.goal_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at != None  
                }
            }
        else:
            return {
                "task": {
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": task.completed_at != None  
                    }
                }
    
    elif request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]

        db.session.commit()

        return jsonify({
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at != None  
            }
        })

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify({
        "details": (f'Task {task.task_id} "{task.title}" successfully deleted')
        })


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_mark_complete(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response(f"Task {task_id} not found", 404)
    
    if request.method == "PATCH":
        task.completed_at = datetime.now()
        
        db.session.commit()

        SLACK_API_KEY = os.environ.get("SLACK_API_KEY")

        header={"Authorization": SLACK_API_KEY} 

        path = "https://slack.com/api/chat.postMessage"

        query_params= {
            "channel": "slack-api-test-channel",
            "text": f"Someone just completed the task {task.title}"
        }

        requests.post(path, data=query_params, headers=header)  

        return jsonify({
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at != None
            }
        })

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_mark_incomplete(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response(f"Task {task_id} not found", 404)
    
    if request.method == "PATCH":
        task.completed_at = None
        
        db.session.commit()

        return jsonify({
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at != None
            }
        })


goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["GET", "POST"])
def handle_goals():
    
    if request.method == "GET":
        goals = Goal.query.all()

        goals_response = []
        for goal in goals:
            goals_response.append({
                "id": goal.goal_id,
                "title": goal.title    
                })

        return jsonify(goals_response), 200

    elif request.method == "POST":
        request_body = request.get_json()
        
        if "title" not in request_body:

            return jsonify({
                "details": "Invalid data"
            }), 400

        new_goal = Goal(title=request_body["title"])

        db.session.add(new_goal)
        db.session.commit()

        return jsonify(
            {
                "goal": {
                "id": new_goal.goal_id,
                "title": new_goal.title
                }
            }), 201
    

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if goal is None:
        return make_response(f"Goal {goal_id} not found", 404)

    if request.method == "GET":
        return {
            "goal": {
                "id": goal.goal_id,
                "title": goal.title,
                }
            }
    
    elif request.method == "PUT":
        form_data = request.get_json()

        goal.title = form_data["title"]

        db.session.commit()

        return jsonify({
        "goal": {
            "id": goal.goal_id,
            "title": goal.title
            
            }
        })

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()

        return jsonify({
        "details": (f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted")
        })


@goals_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goal_tasks(goal_id):
    
    goal = Goal.query.get(goal_id)

    if goal is None:
        return make_response(f"Goal {goal_id} not found", 404)

    if request.method == "GET":
        tasks = goal.tasks 

        if tasks == []:
            return {
                    "id": int(goal_id),
                    "title": goal.title,
                    "tasks": tasks
                    }
        else:
            tasks_list = []
            for task in tasks:
                tasks_list.append(
                    {
                    "id": task.task_id,
                    "goal_id": task.goal_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": task.completed_at != None 
                    })

            return {
                    "id": int(goal_id),
                    "title": goal.title,
                    "tasks": tasks_list
                    }
            
    
    elif request.method == "POST":
        form_data = request.get_json()

        for task_id in form_data["task_ids"]:
            task = Task.query.get(task_id)
            task.goal_id = goal_id

        db.session.commit()

        return jsonify({
                    "id": int(goal_id),
                    "task_ids": form_data["task_ids"]
                })

     