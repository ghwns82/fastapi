from functools import lru_cache
import os
from dotenv import load_dotenv

import insightface
from insightface.app import FaceAnalysis
from pinecone import Pinecone

# 로딩
@lru_cache(maxsize=1)
def get_models(ctx_id: int = -1):
    # print('모델 설치 중')
    # model_pack_name = 'buffalo_l'
    # app = FaceAnalysis(name=model_pack_name)
    print('모델 로딩 중')
    det = insightface.model_zoo.retinaface.RetinaFace("model/det_10g.onnx")
    rec = insightface.model_zoo.arcface_onnx.ArcFaceONNX("model/w600k_mbf.onnx")
    det.prepare(ctx_id=ctx_id)  # CPU:-1, GPU:0
    rec.prepare(ctx_id=ctx_id)
    print('모델 로딩 완료')
    return det, rec

@lru_cache(maxsize=1)
def get_database():
    print('데이터베이스 로딩 중')
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    HOST = os.getenv("HOST")

    pc = Pinecone(api_key=API_KEY)
    index = pc.Index(host=HOST)

    print('데이터베이스 로딩 완료')
    return pc, index



