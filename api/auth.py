"""
API Endpoints para autenticación
"""
import uuid
import re
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator, Field
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt

from models.database import get_db
from models.user import User

router = APIRouter(prefix="/auth", tags=["Autenticación"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Configuración JWT
SECRET_KEY = "evaluai-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


# ============= SCHEMAS =============

class UserRegister(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    full_name: str
    institution: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Email inválido')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v):
        # bcrypt tiene límite de 72 bytes
        if len(v.encode('utf-8')) > 72:
            raise ValueError('La contraseña no puede exceder 72 caracteres')
        return v


class UserLogin(BaseModel):
    email: str
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Email inválido')
        return v.lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


# ============= FUNCIONES AUXILIARES =============

def hash_password(password: str) -> str:
    """
    Genera hash de contraseña usando bcrypt.
    Trunca a 72 bytes si es necesario (límite de bcrypt).
    """
    # bcrypt limita a 72 bytes, truncar si es necesario
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash.
    Trunca a 72 bytes si es necesario para consistencia.
    """
    # Aplicar mismo truncamiento que en hash_password
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verifica un token JWT y retorna el payload"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
) -> User:
    """Obtiene el usuario actual desde el token"""
    user_id = token_data.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return user


# ============= ENDPOINTS =============

@router.post("/register", response_model=dict)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario (profesor)
    """
    try:
        # Verificar si el email ya existe
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está registrado"
            )
        
        # Crear nuevo usuario
        new_user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            institution=user_data.institution or "",
            plan_type="profesor",
            word_limit=120000,
            words_used=0,
            extra_blocks=0,
            is_active=True,
            is_paid=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generar token
        access_token = create_access_token(data={"sub": new_user.id})
        
        return {
            "success": True,
            "message": "Usuario registrado exitosamente",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "institution": new_user.institution,
                "words_available": new_user.words_available,
                "words_used": new_user.words_used
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR en registro: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al registrar usuario: {str(e)}"
        )


@router.post("/login", response_model=dict)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Inicia sesión y retorna token
    """
    try:
        # Buscar usuario
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )
        
        # Generar token
        access_token = create_access_token(data={"sub": user.id})
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "institution": user.institution,
                "words_available": user.words_available,
                "words_used": user.words_used,
                "extra_blocks": user.extra_blocks
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR en login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al iniciar sesión: {str(e)}"
        )


@router.post("/verify", response_model=dict)
async def verify_token_endpoint(token_data: dict = Depends(verify_token)):
    """
    Verifica si un token es válido
    """
    return {
        "success": True,
        "valid": True,
        "user_id": token_data.get("sub"),
        "expires": token_data.get("exp")
    }


@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Obtiene información del usuario actual
    """
    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "institution": current_user.institution,
            "words_available": current_user.words_available,
            "words_used": current_user.words_used,
            "extra_blocks": current_user.extra_blocks,
            "plan_type": current_user.plan_type,
            "is_active": current_user.is_active
        }
    }
