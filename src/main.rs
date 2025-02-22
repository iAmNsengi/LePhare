use actix_web::{
    delete, get, post, put,
    web::{Data, Json, Path},
    App, HttpResponse, HttpServer, Responder,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use std::collections::HashMap;
use uuid::Uuid;

// Define the Todo struct that represents our todo item
#[derive(Debug, Serialize, Deserialize, Clone)]
struct Todo {
    id: Uuid,
    title: String,
    description: Option<String>,
    completed: bool,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

// Define the request payload for creating/updating todos
#[derive(Debug, Deserialize)]
struct TodoRequest {
    title: String,
    description: Option<String>,
}

struct AppState {
    todos: Mutex<HashMap<Uuid, Todo>>,
}

#[post("/todos")]
async fn create_todo(state: Data<AppState>, todo_req: Json<TodoRequest>) -> impl Responder {
    let mut todos = state.todos.lock().unwrap();
    
    let new_todo = Todo {
        id: Uuid::new_v4(),
        title: todo_req.title.clone(),
        description: todo_req.description.clone(),
        completed: false,
        created_at: Utc::now(),
        updated_at: Utc::now(),
    };
    
    let todo_id = new_todo.id;
    todos.insert(todo_id, new_todo.clone());
    
    HttpResponse::Created().json(new_todo)
}

#[get("/todos")]
async fn get_todos(state: Data<AppState>) -> impl Responder {
    let todos = state.todos.lock().unwrap();
    let todos_vec: Vec<&Todo> = todos.values().collect();
    
    HttpResponse::Ok().json(todos_vec)
}

#[get("/todos/{id}")]
async fn get_todo(state: Data<AppState>, path: Path<Uuid>) -> impl Responder {
    let todos = state.todos.lock().unwrap();
    let todo_id = path.into_inner();
    
    match todos.get(&todo_id) {
        Some(todo) => HttpResponse::Ok().json(todo),
        None => HttpResponse::NotFound().json("Todo not found"),
    }
}

#[put("/todos/{id}")]
async fn update_todo(
    state: Data<AppState>,
    path: Path<Uuid>,
    todo_req: Json<TodoRequest>,
) -> impl Responder {
    let mut todos = state.todos.lock().unwrap();
    let todo_id = path.into_inner();
    
    if let Some(todo) = todos.get_mut(&todo_id) {
        todo.title = todo_req.title.clone();
        todo.description = todo_req.description.clone();
        todo.updated_at = Utc::now();
        
        HttpResponse::Ok().json(todo)
    } else {
        HttpResponse::NotFound().json("Todo not found")
    }
}

#[put("/todos/{id}/toggle")]
async fn toggle_todo(state: Data<AppState>, path: Path<Uuid>) -> impl Responder {
    let mut todos = state.todos.lock().unwrap();
    let todo_id = path.into_inner();
    
    if let Some(todo) = todos.get_mut(&todo_id) {
        todo.completed = !todo.completed;
        todo.updated_at = Utc::now();
        
        HttpResponse::Ok().json(todo)
    } else {
        HttpResponse::NotFound().json("Todo not found")
    }
}

#[delete("/todos/{id}")]
async fn delete_todo(state: Data<AppState>, path: Path<Uuid>) -> impl Responder {
    let mut todos = state.todos.lock().unwrap();
    let todo_id = path.into_inner();
    
    if todos.remove(&todo_id).is_some() {
        HttpResponse::NoContent().finish()
    } else {
        HttpResponse::NotFound().json("Todo not found")
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize logger
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));
    
    // Create app state
    let app_state = Data::new(AppState {
        todos: Mutex::new(HashMap::new()),
    });
    
    // Start HTTP server
    HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .service(create_todo)
            .service(get_todos)
            .service(get_todo)
            .service(update_todo)
            .service(toggle_todo)
            .service(delete_todo)
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}