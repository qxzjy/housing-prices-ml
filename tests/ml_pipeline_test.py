import os
import pytest
import pandas as pd
from app.train import load_data, preprocess_data, create_pipeline, train_and_log_model
from unittest import mock
from sqlalchemy import create_engine


# Test data loading
def test_load_data():
    engine = create_engine(os.getenv("DB_URI"), echo=True)

    with engine.connect() as conn :
        dataset = pd.read_sql("SELECT * FROM housing_prices", conn, index_col="id")
    assert not dataset.empty, "Dataframe is empty"

# Test data preprocessing
def test_preprocess_data():
    dataset = load_data()
    X_train, X_test, y_train, y_test = preprocess_data(dataset)
    assert len(X_train) > 0, "Training data is empty"
    assert len(X_test) > 0, "Test data is empty"

# Test pipeline creation
def test_create_pipeline():
    pipeline = create_pipeline()
    assert "standard_scaler" in pipeline.named_steps, "Standard scaler missing in pipeline"
    assert "lasso" in pipeline.named_steps, "Lasso regressor missing in pipeline"

# Test model training (mocking GridSearchCV)
@mock.patch('app.train.GridSearchCV.fit', return_value=None)
def test_train_model(mock_fit):
    artifact_path = "housing-prices-estimator",
    registered_model_name = "housing-prices-estimator-LR"
    param_grid = {"lasso__alpha": [100]}
    pipe = create_pipeline()
    X_train, X_test, y_train, y_test = preprocess_data(load_data())
    model = train_and_log_model(pipe, X_train, y_train, param_grid, artifact_path, registered_model_name)
    assert model is not None, "Model training failed"