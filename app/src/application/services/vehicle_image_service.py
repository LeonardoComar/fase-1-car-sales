import os
import uuid
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
from pathlib import Path
from app.src.domain.entities.vehicle_image_model import VehicleImage
from app.src.domain.ports.vehicle_image_repository import VehicleImageRepository
from app.src.application.dtos.vehicle_image_dto import (
    VehicleImageResponse, 
    VehicleImagesResponse, 
    ImageUploadResponse
)

class VehicleImageService:
    
    # Configurações
    UPLOAD_DIR = "static/uploads"
    THUMBNAIL_DIR = "static/uploads/thumbnails"
    MAX_IMAGES_PER_VEHICLE = 10
    MIN_IMAGES_PER_VEHICLE = 1
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    THUMBNAIL_SIZE = (300, 300)
    
    def __init__(self, vehicle_image_repository: VehicleImageRepository):
        self.vehicle_image_repository = vehicle_image_repository
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Garantir que os diretórios de upload existam"""
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.THUMBNAIL_DIR).mkdir(parents=True, exist_ok=True)
    
    def _get_vehicle_directory(self, vehicle_type: str, vehicle_id: int) -> str:
        """Obter diretório específico do veículo"""
        return f"{self.UPLOAD_DIR}/{vehicle_type}/{vehicle_id}"
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validar arquivo de upload"""
        # Verificar extensão
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Extensão não permitida. Permitidas: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # Verificar tamanho (se possível)
        if hasattr(file.file, 'seek') and hasattr(file.file, 'tell'):
            file.file.seek(0, 2)  # Ir para o final
            size = file.file.tell()
            file.file.seek(0)  # Voltar ao início
            
            if size > self.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Arquivo muito grande. Máximo: {self.MAX_FILE_SIZE / 1024 / 1024}MB"
                )
    
    def _generate_filename(self, original_filename: str) -> str:
        """Gerar nome único para o arquivo"""
        file_ext = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_ext}"
    
    def _create_thumbnail(self, image_path: str, thumbnail_path: str) -> None:
        """Criar thumbnail da imagem"""
        try:
            with Image.open(image_path) as img:
                # Converter para RGB se necessário
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Redimensionar mantendo proporção
                img.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
        except Exception as e:
            print(f"Erro ao criar thumbnail: {e}")
            # Se falhar, não é crítico - continuar sem thumbnail
    
    def upload_images(self, vehicle_type: str, vehicle_id: int, files: List[UploadFile]) -> List[ImageUploadResponse]:
        """Upload de múltiplas imagens para um veículo"""
        # Verificar se veículo não excederá o limite
        current_count = self.vehicle_image_repository.count_by_vehicle_id(vehicle_id)
        total_after_upload = current_count + len(files)
        
        if total_after_upload > self.MAX_IMAGES_PER_VEHICLE:
            raise HTTPException(
                status_code=400,
                detail=f"Máximo de {self.MAX_IMAGES_PER_VEHICLE} imagens por veículo. "
                       f"Atualmente: {current_count}, tentando adicionar: {len(files)}"
            )
        
        # Criar diretório do veículo
        vehicle_dir = self._get_vehicle_directory(vehicle_type, vehicle_id)
        Path(vehicle_dir).mkdir(parents=True, exist_ok=True)
        
        # Criar diretório de thumbnails do veículo
        thumbnail_dir = f"{self.THUMBNAIL_DIR}/{vehicle_type}/{vehicle_id}"
        Path(thumbnail_dir).mkdir(parents=True, exist_ok=True)
        
        uploaded_images = []
        
        for i, file in enumerate(files):
            # Validar arquivo
            self._validate_file(file)
            
            # Gerar nome único
            filename = self._generate_filename(file.filename)
            
            # Caminhos dos arquivos
            image_path = f"{vehicle_dir}/{filename}"
            thumbnail_filename = f"thumb_{filename}"
            thumbnail_path = f"{thumbnail_dir}/{thumbnail_filename}"
            
            # Salvar arquivo original
            with open(image_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)
            
            # Criar thumbnail
            self._create_thumbnail(image_path, thumbnail_path)
            
            # Calcular posição
            position = current_count + i + 1
            
            # Primeira imagem é primary por padrão se não houver outras
            is_primary = (current_count == 0 and i == 0)
            
            # Salvar no banco
            vehicle_image = VehicleImage(
                vehicle_id=vehicle_id,
                filename=filename,
                path=image_path,
                thumbnail_path=thumbnail_path,
                position=position,
                is_primary=is_primary
            )
            
            saved_image = self.vehicle_image_repository.create(vehicle_image)
            
            # Gerar URL para resposta
            url = f"/static/uploads/{vehicle_type}/{vehicle_id}/{filename}"
            
            uploaded_images.append(ImageUploadResponse(
                id=saved_image.id,
                filename=filename,
                url=url,
                position=position,
                is_primary=is_primary,
                message="Upload realizado com sucesso"
            ))
        
        return uploaded_images
    
    def get_vehicle_images(self, vehicle_id: int, vehicle_type: str) -> VehicleImagesResponse:
        """Obter todas as imagens de um veículo"""
        images = self.vehicle_image_repository.find_by_vehicle_id(vehicle_id)
        
        image_responses = []
        for image in images:
            # Gerar URLs
            url = f"/static/uploads/{vehicle_type}/{vehicle_id}/{image.filename}"
            thumbnail_url = None
            if image.thumbnail_path:
                thumb_filename = f"thumb_{image.filename}"
                thumbnail_url = f"/static/uploads/thumbnails/{vehicle_type}/{vehicle_id}/{thumb_filename}"
            
            image_responses.append(VehicleImageResponse(
                id=image.id,
                vehicle_id=image.vehicle_id,
                filename=image.filename,
                path=image.path,
                url=url,
                thumbnail_path=image.thumbnail_path,
                thumbnail_url=thumbnail_url,
                position=image.position,
                is_primary=image.is_primary,
                uploaded_at=image.uploaded_at
            ))
        
        return VehicleImagesResponse(
            vehicle_id=vehicle_id,
            images=image_responses,
            total_images=len(image_responses)
        )
    
    def delete_image(self, image_id: int) -> bool:
        """Deletar uma imagem e reordenar automaticamente"""
        # Buscar imagem
        image = self.vehicle_image_repository.find_by_id(image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Imagem não encontrada")
        
        # Verificar se não é a última imagem
        current_count = self.vehicle_image_repository.count_by_vehicle_id(image.vehicle_id)
        if current_count <= self.MIN_IMAGES_PER_VEHICLE:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível deletar. Mínimo de {self.MIN_IMAGES_PER_VEHICLE} imagem(ns) por veículo"
            )
        
        # Guardar informações antes da exclusão
        deleted_position = image.position
        deleted_was_primary = image.is_primary
        vehicle_id = image.vehicle_id
        
        # Deletar arquivos físicos
        try:
            if os.path.exists(image.path):
                os.remove(image.path)
            if image.thumbnail_path and os.path.exists(image.thumbnail_path):
                os.remove(image.thumbnail_path)
        except Exception as e:
            print(f"Erro ao deletar arquivos: {e}")
        
        # Deletar do banco
        success = self.vehicle_image_repository.delete_by_id(image_id)
        
        if success:
            # Reordenar imagens automaticamente
            self._reorder_after_deletion(vehicle_id, deleted_position, deleted_was_primary)
        
        return success
    
    def _reorder_after_deletion(self, vehicle_id: int, deleted_position: int, deleted_was_primary: bool):
        """Reordenar imagens após exclusão"""
        # Buscar todas as imagens restantes
        remaining_images = self.vehicle_image_repository.find_by_vehicle_id(vehicle_id)
        
        # Reordenar posições para preencher lacunas
        reorder_updates = []
        new_position = 1
        
        for img in remaining_images:
            if img.position != new_position:
                reorder_updates.append((img.id, new_position))
            new_position += 1
        
        # Aplicar reordenação se necessário
        if reorder_updates:
            self.vehicle_image_repository.update_positions(vehicle_id, reorder_updates)
        
        # Se a imagem deletada era principal, definir nova principal
        if deleted_was_primary and remaining_images:
            # A nova primeira imagem (posição 1) será a principal
            first_image = min(remaining_images, key=lambda x: x.position)
            self.vehicle_image_repository.set_primary_image(vehicle_id, first_image.id)
    
    def set_primary_image(self, vehicle_id: int, image_id: int) -> bool:
        """Definir imagem como principal"""
        return self.vehicle_image_repository.set_primary_image(vehicle_id, image_id)
    
    def reorder_images(self, vehicle_id: int, image_positions: List) -> bool:
        """Reordenar imagens"""
        # Converter de ImagePositionItem para tuplas
        positions_tuples = []
        for item in image_positions:
            if hasattr(item, 'image_id') and hasattr(item, 'position'):
                # É um ImagePositionItem
                positions_tuples.append((item.image_id, item.position))
            else:
                # É uma tupla já
                positions_tuples.append(item)
        
        # Validar posições
        for _, position in positions_tuples:
            if position < 1 or position > self.MAX_IMAGES_PER_VEHICLE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Posição deve estar entre 1 e {self.MAX_IMAGES_PER_VEHICLE}"
                )
        
        return self.vehicle_image_repository.update_positions(vehicle_id, positions_tuples)
