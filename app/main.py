
from http.client import HTTPException
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time


app = FastAPI()

#this is a class to define what we want to send in a POST request
#each variable in this class represents a column in the database. 
#if a variable is added to the class it need to be added to the query for each endpoint
class Post(BaseModel):
    title: str
    content: str
    
   
#connection to database
while True:
        
    try:
        conn = psycopg2.connect(host="", database="", user="", password="", cursor_factory=RealDictCursor)
        cur = conn.cursor() #cursor
        print("Database connection was successful")

        break #if a connection is made it will break out of the while loop

    except Exception as error:
        print("connection to database failed")
        print("Error: ", error)
        time.sleep(2)


#this is the root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome"}


#get posts (READ)
@app.get("/posts")
async def get_posts():
    cur.execute("""SELECT * FROM posts""")
    posts = cur.fetchall() #fetchall gets all posts fetch one would be used for only one post
    return {"data": posts}
    
#post posts (CREATE)
@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(post: Post):
    cur.execute("""INSERT INTO posts (title, content) VALUES (%s, %s) RETURNing * """, (post.title, post.content)) #%s protects against SQL injection
    new_post = cur.fetchone() 
    conn.commit() #save to database
    return {"data": new_post}


# get posts (READ id)
@app.get("/posts/{id}")
async def get_post(id: int): #convert id to int so that a valid id is passed
    cur.execute(""" SELECT * FROM posts WHERE id = %s""", (str(id))) #convert id back to string to run query
    post = cur.fetchone()
    if not post: #check to see that there is a post with the id we are calling
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
    return {"post_detail" : post}


#delete posts (DELETE id)
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    cur.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cur.fetchone()
    conn.commit()
    #index = find_index_post(id)
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail = f"post with id: {id} does not exist")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    

#update posts (PUT id) not finished
@app.put("/posts/{id}")
async def update_post(id: int, post:Post):
    cur.execute("""UPDATE posts SET title = %s, content = %s WHERE id = %s RETURNING *""", (post.title, post.content, str(id)))
    updated_post = cur.fetchone()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} does not exist")
    conn.commit()
    return{"data": updated_post}
