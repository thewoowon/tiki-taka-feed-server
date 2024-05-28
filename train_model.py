import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.multioutput import MultiOutputClassifier
import joblib
import os

# 데이터 로드
data = pd.read_csv("train.csv")

# 학습 데이터와 테스트 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(
    data["title"], data[["job", "language"]], test_size=0.2, random_state=42
)

# 파이프라인 생성
model = make_pipeline(TfidfVectorizer(), MultiOutputClassifier(LogisticRegression()))

# 모델 학습
model.fit(X_train, y_train)

# 테스트 데이터로 모델 평가
y_pred = model.predict(X_test)

# 개별적으로 평가 보고서 생성
for i, column in enumerate(y_test.columns):
    print(f"Classification Report for {column}:")
    print(classification_report(y_test[column], y_pred[:, i]))

# 모델 저장
model_path = os.path.join("app", "text_classification_model.pkl")
joblib.dump(model, model_path)
