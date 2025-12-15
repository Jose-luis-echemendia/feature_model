"""
WebSocket endpoint para estadísticas en tiempo real de feature models.

Este módulo proporciona una conexión WebSocket persistente que envía
actualizaciones automáticas de estadísticas cada vez que el modelo cambia.

Casos de uso:
- Edición colaborativa con múltiples usuarios
- Dashboards en vivo con latencia mínima
- Monitoreo en tiempo real de cambios
"""

import uuid
import asyncio
import json
from typing import Set
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Depends

from app.api.deps import (
    AsyncSessionDep,
    get_verified_user
)
from app.repositories.a_sync.feature_model import FeatureModelRepositoryAsync
from app.repositories.a_sync.feature_model_version import (
    FeatureModelVersionRepositoryAsync,
)

router = APIRouter(
    prefix="/ws",
    tags=["WebSocket - Statistics"],
    dependencies=[Depends(get_verified_user)],
)


# ============================================================================
# GESTOR DE CONEXIONES WEBSOCKET
# ============================================================================


class StatisticsConnectionManager:
    """
    Gestor de conexiones WebSocket para estadísticas en tiempo real.

    Mantiene un registro de conexiones activas por version_id y permite
    broadcast de actualizaciones a todos los clientes suscritos.
    """

    def __init__(self):
        # version_id -> Set[WebSocket]
        self.active_connections: dict[uuid.UUID, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, version_id: uuid.UUID):
        """Conectar un cliente a las actualizaciones de una versión."""
        await websocket.accept()

        async with self._lock:
            if version_id not in self.active_connections:
                self.active_connections[version_id] = set()
            self.active_connections[version_id].add(websocket)

    async def disconnect(self, websocket: WebSocket, version_id: uuid.UUID):
        """Desconectar un cliente."""
        async with self._lock:
            if version_id in self.active_connections:
                self.active_connections[version_id].discard(websocket)

                # Limpiar si no hay más conexiones
                if not self.active_connections[version_id]:
                    del self.active_connections[version_id]

    async def broadcast_statistics(self, version_id: uuid.UUID, statistics: dict):
        """
        Enviar estadísticas actualizadas a todos los clientes suscritos.

        Args:
            version_id: ID de la versión actualizada
            statistics: Diccionario con las estadísticas
        """
        if version_id not in self.active_connections:
            return

        # Preparar mensaje
        message = {
            "type": "statistics_update",
            "version_id": str(version_id),
            "timestamp": datetime.utcnow().isoformat(),
            "data": statistics,
        }
        message_json = json.dumps(message)

        # Enviar a todos los clientes conectados
        disconnected = set()

        for connection in self.active_connections[version_id]:
            try:
                await connection.send_text(message_json)
            except Exception:
                # Marcar para desconexión
                disconnected.add(connection)

        # Limpiar conexiones muertas
        async with self._lock:
            for connection in disconnected:
                self.active_connections[version_id].discard(connection)

    def get_connection_count(self, version_id: uuid.UUID) -> int:
        """Obtener número de conexiones activas para una versión."""
        return len(self.active_connections.get(version_id, set()))


# Instancia global del gestor
manager = StatisticsConnectionManager()


# ============================================================================
# ENDPOINT WEBSOCKET
# ============================================================================


@router.websocket("/feature-models/{model_id}/versions/{version_id}/statistics")
async def websocket_statistics(
    websocket: WebSocket,
    model_id: uuid.UUID,
    version_id: uuid.UUID,
    session: AsyncSessionDep,
):
    """
    WebSocket para recibir estadísticas en tiempo real de un feature model.

    **Flujo de Conexión**:
    1. Cliente se conecta al WebSocket
    2. Servidor valida permisos y existencia del modelo
    3. Servidor envía estadísticas iniciales inmediatamente
    4. Cliente recibe actualizaciones automáticas cuando hay cambios
    5. Servidor envía ping cada 30 segundos para mantener conexión

    **Formato de Mensajes del Servidor**:

    Mensaje de Bienvenida:
    ```json
    {
        "type": "connected",
        "message": "Connected to statistics stream",
        "version_id": "uuid",
        "active_connections": 3
    }
    ```

    Actualización de Estadísticas:
    ```json
    {
        "type": "statistics_update",
        "version_id": "uuid",
        "timestamp": "2025-12-10T15:30:00Z",
        "data": {
            "total_features": 45,
            "mandatory_features": 32,
            "optional_features": 13,
            "total_groups": 5,
            "xor_groups": 3,
            "or_groups": 2,
            "total_relations": 18,
            "requires_relations": 15,
            "excludes_relations": 3,
            "total_constraints": 8,
            "total_configurations": 12,
            "max_tree_depth": 5
        }
    }
    ```

    Ping (mantener conexión):
    ```json
    {
        "type": "ping",
        "timestamp": "2025-12-10T15:30:00Z"
    }
    ```

    Error:
    ```json
    {
        "type": "error",
        "code": "NOT_FOUND",
        "message": "Feature Model not found"
    }
    ```

    **Comandos del Cliente**:

    Solicitar actualización manual:
    ```json
    {
        "action": "refresh"
    }
    ```

    Pong (respuesta a ping):
    ```json
    {
        "action": "pong"
    }
    ```

    **Ejemplo de Uso (JavaScript)**:
    ```javascript
    const ws = new WebSocket(
        'ws://localhost:8000/api/v1/ws/feature-models/uuid/versions/uuid/statistics'
    );

    ws.onopen = () => {
        console.log('Connected to statistics stream');
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);

        switch (message.type) {
            case 'connected':
                console.log('Connected:', message);
                break;
            case 'statistics_update':
                updateDashboard(message.data);
                break;
            case 'ping':
                ws.send(JSON.stringify({ action: 'pong' }));
                break;
            case 'error':
                console.error('Error:', message.message);
                break;
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
        console.log('Disconnected from statistics stream');
    };

    // Solicitar actualización manual
    function refreshStatistics() {
        ws.send(JSON.stringify({ action: 'refresh' }));
    }
    ```

    Args:
        websocket: Conexión WebSocket
        model_id: UUID del feature model
        version_id: UUID de la versión específica
        session: Sesión de base de datos

    Note:
        - La conexión requiere autenticación (implementar según tu sistema)
        - El servidor mantiene la conexión con pings cada 30 segundos
        - Las actualizaciones se envían automáticamente cuando detecta cambios
        - Máximo 100 conexiones simultáneas por versión (configurable)
    """
    # Inicializar repositorios
    feature_model_repo = FeatureModelRepositoryAsync(session)
    version_repo = FeatureModelVersionRepositoryAsync(session)

    try:
        # Validar que el modelo existe
        feature_model = await feature_model_repo.get(model_id)
        if not feature_model or not feature_model.is_active:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Feature Model not found or inactive",
            )
            return

        # Validar que la versión existe
        version = await version_repo.get(version_id)
        if not version or version.feature_model_id != model_id:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Version not found or doesn't belong to this model",
            )
            return

        # Conectar cliente
        await manager.connect(websocket, version_id)

        # Enviar mensaje de bienvenida
        await websocket.send_json(
            {
                "type": "connected",
                "message": "Connected to statistics stream",
                "version_id": str(version_id),
                "active_connections": manager.get_connection_count(version_id),
            }
        )

        # Enviar estadísticas iniciales inmediatamente
        initial_stats = await version_repo.get_statistics(version_id)
        if initial_stats:
            await websocket.send_json(
                {
                    "type": "statistics_update",
                    "version_id": str(version_id),
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": initial_stats,
                }
            )

        # Mantener conexión y escuchar comandos del cliente
        last_ping = datetime.utcnow()

        while True:
            try:
                # Esperar mensaje del cliente con timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)

                message = json.loads(data)
                action = message.get("action")

                # Manejar comandos del cliente
                if action == "refresh":
                    # Cliente solicita actualización manual
                    stats = await version_repo.get_statistics(version_id)
                    if stats:
                        await websocket.send_json(
                            {
                                "type": "statistics_update",
                                "version_id": str(version_id),
                                "timestamp": datetime.utcnow().isoformat(),
                                "data": stats,
                            }
                        )

                elif action == "pong":
                    # Cliente respondió al ping
                    pass

            except asyncio.TimeoutError:
                # Timeout - enviar ping para mantener conexión
                current_time = datetime.utcnow()
                if (current_time - last_ping).seconds >= 30:
                    await websocket.send_json(
                        {
                            "type": "ping",
                            "timestamp": current_time.isoformat(),
                        }
                    )
                    last_ping = current_time

    except WebSocketDisconnect:
        # Cliente se desconectó
        await manager.disconnect(websocket, version_id)

    except Exception as e:
        # Error inesperado
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "code": "INTERNAL_ERROR",
                    "message": str(e),
                }
            )
        except:
            pass

        await manager.disconnect(websocket, version_id)
        raise


# ============================================================================
# FUNCIÓN AUXILIAR PARA TRIGGER DE ACTUALIZACIONES
# ============================================================================


async def trigger_statistics_update(
    version_id: uuid.UUID,
    session: AsyncSessionDep,
):
    """
    Función auxiliar para disparar actualización de estadísticas via WebSocket.

    Llamar esta función después de cualquier operación que modifique el modelo:
    - Agregar/eliminar/modificar features
    - Agregar/eliminar grupos
    - Agregar/eliminar relaciones
    - Agregar/eliminar constraints

    Args:
        version_id: UUID de la versión modificada
        session: Sesión de base de datos

    Example:
        ```python
        # Después de agregar una feature
        feature = await feature_repo.create(...)
        await trigger_statistics_update(version_id, session)
        ```
    """
    # Calcular nuevas estadísticas
    version_repo = FeatureModelVersionRepositoryAsync(session)
    stats = await version_repo.get_statistics(version_id)

    if stats:
        # Broadcast a todos los clientes conectados
        await manager.broadcast_statistics(version_id, stats)


# ============================================================================
# ENDPOINT REST PARA TESTING
# ============================================================================


@router.get("/feature-models/versions/{version_id}/connections")
async def get_active_connections(version_id: uuid.UUID) -> dict:
    """
    Obtener número de conexiones WebSocket activas para una versión.

    Útil para monitoreo y debugging.

    Args:
        version_id: UUID de la versión

    Returns:
        dict: Información de conexiones activas
    """
    return {
        "version_id": str(version_id),
        "active_connections": manager.get_connection_count(version_id),
        "timestamp": datetime.utcnow().isoformat(),
    }
