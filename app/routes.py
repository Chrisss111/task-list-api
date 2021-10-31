from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response, request
from datetime import datetime



tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    # print("inside of handle task")
    if request.method == "GET":
        # title_query = request.args.get("title")
        # description_query = request.args.get("description")

        #add re making query more flexible and add is_completed
        sort_query = request.args.get("sort")
        
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())
         

        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc())
            
            
        # elif title_query:
        #     tasks = Task.query.filter(Task.title.contains(title_query))
            

        # elif description_query:
        #     tasks = Task.query.filter_by(description=description_query)
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
        # print(new_task)

        

        return jsonify(
            {
                "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": new_task.completed_at != None  
                }
            }), 201
    # how make status code= to a specfic numebr? mine is eqyal to 200 but test wants 201

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response(f"Task {task_id} not found", 404)

    if request.method == "GET":
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

#wave 3

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_mark_complete(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response(f"Task {task_id} not found", 404)
    
    if request.method == "PATCH":
        # form_data = request.get_json()

        task.completed_at = datetime.now()
        

        db.session.commit()

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


# ##########
#goal routes (wave 5)

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["GET", "POST"])
def handle_goals():
    # print("inside of handle task")
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

