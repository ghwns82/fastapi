from functools import lru_cache
import os
from dotenv import load_dotenv

import insightface
from pinecone import Pinecone

# 로딩

@lru_cache(maxsize=1)
def get_models(ctx_id: int = -1):
    print('모델 설치 중')
    model_pack_name = 'buffalo_l'
    app = FaceAnalysis(name=model_pack_name)
    print('모델 로딩 중')
    det = insightface.model_zoo.retinaface.RetinaFace("buffalo_l/det_10g.onnx")
    rec = insightface.model_zoo.arcface_onnx.ArcFaceONNX("buffalo_l/w600k_r50.onnx")
    det.prepare(ctx_id=ctx_id)  # CPU:-1, GPU:0
    rec.prepare(ctx_id=ctx_id)
    print('모델 로딩 완료')
    return det, rec

@lru_cache(maxsize=1)
def get_database():
    print('데이터베이스 로딩 중')
    load_dotenv()
    API_KEY = os.getenv("API_KEY")

    pc = Pinecone(api_key=API_KEY)
    index = pc.Index(host="https://facerecsystem-vatdgkb.svc.aped-4627-b74a.pinecone.io")

    print('데이터베이스 로딩 완료')
    return pc, index



