from datetime import datetime, timedelta, timezone

import numpy as np
import cv2

from fastapi import APIRouter, File, Form, UploadFile
from utils import get_models, get_database

from insightface.utils import face_align

from attendance import insert_data


service_router = APIRouter()



def extract_face_embedding(img):
    det, rec = get_models()
    boxes, kpss = det.detect(img, input_size=(640, 640))
    bat=[]
    if boxes is not None:
        for kps in kpss:
            align_img = face_align.norm_crop(img, landmark=kps, image_size=112)
            bat.append(align_img)
    if bat:
        embedding = rec.get_feat(bat).flatten()
        return embedding




@service_router.post('/regist')
async def regist_image(
    student_name: str = Form(...),             # 텍스트
    student_id: str = Form(...),             # 텍스트
    file: UploadFile = File(...),      # 이미지 파일
):
    # 1) 바이트 읽기
    contents = await file.read()

    # 2) OpenCV로 디코딩 (BGR 채널)
    np_arr = np.frombuffer(contents, np.uint8)
    upload_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)  # 또는 IMREAD_UNCHANGED

    if upload_img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    
    #3) 얼굴 임베딩 검출
    embedding = extract_face_embedding(upload_img)

    #4) 벡터 데이터 베이스에 업로드
    pc, index = get_database()
    korea = timezone(timedelta(hours=9))
    now = datetime.now(korea).strftime("%Y-%m-%d %H:%M:%S")
    index.upsert(
        vectors=[
            {
            'id':student_id,
            "values": embedding, 
            "metadata": {"registed date": now, 'student_name':student_name,'student_id':student_id,}
            },
    ])

    return {
        "message": f"Received student_name: {student_name}, student_id: {student_id}, image: {file.filename}",
        "shape": upload_img.shape,
    }


@service_router.post("/predict")
async def classify_image(file: UploadFile = File(...)):
    # 1) 바이트 읽기
    contents = await file.read()

    # 2) OpenCV로 디코딩 (BGR 채널)
    np_arr = np.frombuffer(contents, np.uint8)
    upload_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)  # 또는 IMREAD_UNCHANGED

    if upload_img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    
    #3) 얼굴 임베딩 검출
    embedding = extract_face_embedding(upload_img)

    #4) 벡터 데이터 베이스에 쿼리
    pc, index = get_database()

    result = index.query(
        vector=embedding.astype("float32").ravel().tolist(),     # 검색 기준 벡터
        top_k=1,                 # 상위 1개 결과 반환
        include_metadata=True,   # metadata 포함 여부
    )

    match = result["matches"][0]
    print(f"id: {match['id']}")
    print(f"Score: {match['score']}")
    print(f"Metadata: {match['metadata']}")
    print("------")
    answer = {}
    if match['score'] > 0.2:
        answer['student_id'] = match['metadata']['student_id']
        answer['student_name'] = match['metadata']['student_name']
        answer['score'] = match['score']

        insert_data(answer['student_id'], answer['student_name'])
    else:
        answer['student_id'] = 'unknown'
        answer['score'] = match['score']
    return answer