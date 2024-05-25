import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# 데이터 로드
data = pd.read_csv('train.csv')

# 학습 데이터와 테스트 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(data['text'], data['category'], test_size=0.2, random_state=42)

# 파이프라인 생성
model = make_pipeline(TfidfVectorizer(), LogisticRegression())

# 모델 학습
model.fit(X_train, y_train)

# 테스트 데이터로 모델 평가
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# 모델 저장
model_path = os.path.join('app', 'text_classification_model.pkl')
joblib.dump(model, model_path)
