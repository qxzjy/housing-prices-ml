import pandas as pd
import time
import mlflow
import os
from mlflow.models.signature import infer_signature
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sqlalchemy import create_engine


def load_data() -> pd.DataFrame:
    """
    Load housing prices table from the database specified by the DB_URI environment variable.

    Returns:
        pd.DataFrame: DataFrame containing the 'housing_prices' table with index column 'id'.

    Raises:
        ValueError: If the DB_URI environment variable is not set.
        RuntimeError: If a connection or query error occurs.
    """
    db_uri = os.getenv("DB_URI")
    if not db_uri:
        raise ValueError("DB_URI environment variable is not set")

    engine = create_engine(db_uri, echo=True)

    try:
        with engine.connect() as conn:
            df = pd.read_sql("SELECT * FROM housing_prices", conn, index_col="id")
    except Exception as e:
        raise RuntimeError(f"Failed to load data from database: {e}") from e
    finally:
        try:
            engine.dispose()
        except Exception:
            pass

    return df


def preprocess_data(dataset: pd.DataFrame) -> tuple:
    """
    Preprocess the dataset by separating features and target variable, renaming columns.

    Args:
        dataset (pd.DataFrame): Input DataFrame containing housing data.

    Returns:
        tuple: Contains (X_train, X_test, y_train, y_test) split datasets.

    Raises:
        ValueError: If required columns are missing from the dataset.
    """
    target_variable = "price"

    if target_variable not in dataset.columns:
        raise ValueError(f"Target variable '{target_variable}' not found in dataset")

    X = dataset.drop([target_variable], axis=1)
    try:
        X = X.set_axis(["square_feet", "num_bedrooms", "num_bathrooms", "num_floors", 
                       "year_built", "has_garden", "has_pool", "garage_size", 
                       "location_score", "distance_to_center"], axis=1)
    except ValueError as e:
        raise ValueError(f"Failed to set column names: {e}")
    
    y = dataset[target_variable]
    return train_test_split(X, y, test_size=0.2, random_state=3)


def create_pipeline() -> Pipeline:
    """
    Create a scikit-learn pipeline with StandardScaler and Lasso regression.

    Returns:
        Pipeline: Scikit-learn pipeline object.
    """
    return Pipeline(steps=[
        ("standard_scaler", StandardScaler()),
        ("lasso", Lasso())
    ], verbose=True)


def train_model(pipeline: Pipeline, X_train: pd.DataFrame, y_train: pd.Series, 
                param_grid: dict, cv: int = 3) -> GridSearchCV:
    """
    Train model using GridSearchCV with the specified pipeline and parameters.

    Args:
        pipeline (Pipeline): Scikit-learn pipeline.
        X_train (pd.DataFrame): Training features.
        y_train (pd.Series): Training target values.
        param_grid (dict): Parameters for grid search.
        cv (int, optional): Number of cross-validation folds. Defaults to 3.

    Returns:
        GridSearchCV: Fitted grid search object.

    Raises:
        ValueError: If input parameters are invalid.
    """
    if not isinstance(param_grid, dict):
        raise ValueError("param_grid must be a dictionary")

    model = GridSearchCV(pipeline, param_grid, cv=cv, scoring="r2")
    try:
        model.fit(X_train, y_train)
    except Exception as e:
        raise RuntimeError(f"Model training failed: {e}")
    return model


def log_model(model: GridSearchCV, X_train: pd.DataFrame, 
              artifact_path: str, registered_model_name: str) -> None:
    """
    Log the trained model to MLflow.

    Args:
        model (GridSearchCV): Trained model to log.
        X_train (pd.DataFrame): Training features for signature inference.
        artifact_path (str): Path where model artifacts will be stored.
        registered_model_name (str): Name under which to register the model.

    Raises:
        ValueError: If input parameters are invalid.
    """
    if not artifact_path or not registered_model_name:
        raise ValueError("artifact_path and registered_model_name must not be empty")

    try:
        predictions = model.predict(X_train)
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path=artifact_path,
            registered_model_name=registered_model_name,
            signature=infer_signature(X_train, predictions)
        )
    except mlflow.exceptions.MlflowException as e:
        print("⚠️ Model logging failed:", e)
    except Exception as e:
        print(f"⚠️ Unexpected error during model logging: {e}")


if __name__ == "__main__":

    param_grid = {
        "lasso__alpha": [i for i in range(100, 1000, 25)]
    }
    
    print("Training model...")
    
    # Time execution
    start_time = time.time()

    # Call mlflow autolog
    mlflow.sklearn.autolog(log_models=False) # We won't log models right away

    # Load data from DB
    dataset = load_data()

    # X, y split
    X_train, X_test, y_train, y_test = preprocess_data(dataset)
    
    # Pipeline
    pipeline = create_pipeline()

    # Log experiment to MLFlow
    with mlflow.start_run() as run:
        model = train_model(pipeline, X_train, y_train, param_grid)
        log_model(model, X_train, "housing-prices-estimator", "housing-prices-estimator-LR")
        
    print("...Done!")
    print(f"---Total training time: {time.time()-start_time}")