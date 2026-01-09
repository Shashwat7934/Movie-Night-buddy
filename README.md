# **Movie Night Buddy: A Context-Aware Movie Recommendation System**

Ever find yourself scrolling endlessly, unsure what to watch? **Movie Night Buddy** is here to help\! This project is a unique movie recommendation system that goes beyond simple genre matching. It suggests movies tailored to your current **mood**, the **weather** outside, and even the **day of the week**, ensuring you find the perfect film for any occasion.

## **📊 The Data**

This recommendation system is built upon a rich dataset comprised of three core files:

* **movie.csv**: Contains movie information, including movieId, title, and genres.  
* **rating.csv**: Includes user ratings for various movies, which are used to calculate an avg\_rating for each film.  
* **tag.csv**: Provides user-generated tags for movies, offering deeper insights into the movie's themes and content.

## **⚙️ How It Works**

The magic of Movie Night Buddy lies in its context-aware filtering and feature engineering.

### **1\. Data Preparation & Feature Engineering**

* **Data Merging**: The three datasets are merged into a single comprehensive DataFrame.  
* **Feature Extraction**:  
  * The year of the movie is extracted from the title.  
  * genres are parsed into a list.  
  * avg\_rating is calculated for each movie to gauge its popularity and quality.  
* **Mood Analysis**: User tags are analyzed to assign one or more "moods" (e.g., **happy, sad, romantic**) to each movie based on a predefined keyword dictionary.  
* **Contextual Mapping**:  
  * **Weather**: Specific genres are mapped to weather conditions (e.g., "rainy" maps to "Romance" and "Drama").  
  * **Day of the Week**: Genres are also associated with days of the week to match the typical vibe (e.g., "Friday" maps to "Thriller" and "Action").

### **2\. The Recommendation Engine**

The core of the project is the get\_recommended\_movies function. Here’s the step-by-step logic:

1. **User Input**: The system takes your current mood, the weather\_condition, and the day\_of\_week as input.  
2. **Mood Filtering**: It first filters the entire movie database to find films that match your selected mood.  
3. **Contextual Genre Filtering**: From the mood-filtered list, it then selects movies whose genres align with the predefined genres for the given weather and day.  
4. **Ranking**: Finally, the filtered movies are sorted by their avg\_rating in descending order.  
5. **Output**: The function returns the **top 10 recommended movies** that best fit your specific context.

## **🚀 Usage**

After running the data processing notebook, the final processed\_movie\_data.csv is generated. The recommendation function can then be used to get personalized suggestions.

**Example:**

\# Get recommendations for a happy mood on a sunny Friday  
recommendations \= get\_recommended\_movies(  
    user\_mood="happy",  
    weather\_condition="sunny",  
    day\_of\_week="Friday",  
    df=movie\_data  
)

print(recommendations)

## **📦 Dependencies**

* pandas  
* NumPy  
* scikit-learn (for potential future vector-based similarity models)