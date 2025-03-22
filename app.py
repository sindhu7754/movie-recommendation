from flask import Flask,request,render_template
import pickle
import requests
import pandas as pd
import difflib

movies=pickle.load(open('model/movies_list.pkl','rb'))
print(movies.shape)
similarity=pickle.load(open('model/similarity.pkl','rb'))

def fetch_poster(movie_id):
   print(movie_id)
   url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
   data = requests.get(url)
   data = data.json()
   poster_path = data['poster_path']
   print(poster_path)
   full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
   return full_path
   
def recommend(movie_name):
  list_of_all_titles=movies['title'].tolist()
  find_close_match=difflib.get_close_matches(movie_name,list_of_all_titles)
  close_match=find_close_match[0]
  index_of_the_movie=movies[movies.title == close_match]['index'].values[0]
  similarity_score=list(enumerate(similarity[index_of_the_movie]))
  sorted_similar_movies=sorted(similarity_score,key=lambda x:x[1],reverse=True)
  print('Movies suggested for you: \n')
  i=1
  recommended_movies_name=[]
  recommended_movies_poster=[]
  for movie in sorted_similar_movies[0:8]:
    index=movie[0]
    title_from_index=movies[movies.index==index]['title'].values[0]
    movie_id=movies[movies.index==index]['id'].values[0]
    recommended_movies_poster.append(fetch_poster(movie_id))
    recommended_movies_name.append(title_from_index)
    print(recommended_movies_name,recommended_movies_poster)
  return recommended_movies_name,recommended_movies_poster
   
      
app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def home():
   
   movie_list=movies['title'].values
   # print(movie_list)
   status=False
   if request.method=="POST":
      try:
         if request.form:
            movies_name=request.form['mname']
            print(movies_name)
            recommended_movies_name,recommended_movies_poster=recommend(movies_name)
            status=True
            return render_template("index.html",movies_name=recommended_movies_name,poster=recommended_movies_poster,movie_list=movie_list,status=status)
      except Exception as e:
         error={'error':e}
         return render_template("index.html",error=error,movie_list=movie_list,status=status)
   else:
      return render_template("index.html",movie_list=movie_list,status=status)

if __name__ == '__main__':
   app.debug=True
   app.run()
