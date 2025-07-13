import pytest
from app.cuentas.domain.value_objects.funcionario import Funcionario, CargoFuncionario, FuncionariosPredefinidos


class TestFuncionarioCreacion:
    """Tests para creación de funcionarios"""
    
    def test_crear_funcionario_basico(self):
        """Test crear funcionario básico"""
        funcionario = Funcionario(
            id_funcionario="JPEREZ001",
            nombre_completo="juan perez",
            cargo=CargoFuncionario.FUNCIONARIO
        )
        assert funcionario.id_funcionario == "JPEREZ001"
        assert funcionario.nombre_completo == "Juan Perez"  # Capitalizado
        assert funcionario.cargo == CargoFuncionario.FUNCIONARIO
    
    def test_crear_funcionario_completo(self):
        """Test crear funcionario con todos los datos"""
        funcionario = Funcionario(
            id_funcionario="MGOMEZ002",
            nombre_completo="Maria Gomez",
            cargo=CargoFuncionario.SUPERVISOR,
            email="maria.gomez@test.com",
            activo=True
        )
        assert funcionario.email == "maria.gomez@test.com"
        assert funcionario.activo == True
    
    def test_validaciones_campos_obligatorios(self):
        """Test validaciones de campos obligatorios"""
        with pytest.raises(ValueError, match="ID.*no puede estar vacío"):
            Funcionario("", "Nombre", CargoFuncionario.FUNCIONARIO)
        
        with pytest.raises(ValueError, match="nombre completo.*no puede estar vacío"):
            Funcionario("ID001", "", CargoFuncionario.FUNCIONARIO)
        
        with pytest.raises(ValueError, match="al menos 3 caracteres"):
            Funcionario("ID001", "AB", CargoFuncionario.FUNCIONARIO)
    
    def test_validacion_email(self):
        """Test validación de email"""
        with pytest.raises(ValueError, match="Email inválido"):
            Funcionario(
                "ID001", "Juan Perez", 
                CargoFuncionario.FUNCIONARIO,
                email="email_invalido"
            )


class TestFuncionarioMetodos:
    """Tests para métodos de funcionario"""
    
    def test_get_nombre_corto(self):
        """Test obtener nombre corto"""
        funcionario = FuncionariosPredefinidos.LUIS_MURCIA
        assert funcionario.get_nombre_corto() == "Luis Fabian"
    
    def test_get_iniciales(self):
        """Test obtener iniciales"""
        funcionario = FuncionariosPredefinidos.LUIS_MURCIA
        assert funcionario.get_iniciales() == "LFMS"
    
    def test_get_cargo_display(self):
        """Test formato de cargo"""
        funcionario = FuncionariosPredefinidos.ANA_RODRIGUEZ
        assert funcionario.get_cargo_display() == "Supervisor"
    
    def test_es_supervisor_o_superior(self):
        """Test verificar si es supervisor o superior"""
        funcionario_base = FuncionariosPredefinidos.LUIS_MURCIA
        supervisor = FuncionariosPredefinidos.ANA_RODRIGUEZ
        admin = FuncionariosPredefinidos.ADMIN_SISTEMA
        
        assert funcionario_base.es_supervisor_o_superior() == False
        assert supervisor.es_supervisor_o_superior() == True
        assert admin.es_supervisor_o_superior() == True
    
    def test_puede_aprobar_procesos(self):
        """Test verificar permisos de aprobación"""
        funcionario = FuncionariosPredefinidos.LUIS_MURCIA
        supervisor = FuncionariosPredefinidos.CARLOS_LOPEZ 
        administrador = FuncionariosPredefinidos.ADMIN_SISTEMA

        assert funcionario.puede_aprobar_procesos() == False
        assert supervisor.puede_aprobar_procesos() == False 
        assert administrador.puede_aprobar_procesos() == True  
    
    def test_es_administrador(self):
        """Test verificar si es administrador"""
        funcionario = FuncionariosPredefinidos.LUIS_MURCIA
        admin = FuncionariosPredefinidos.ADMIN_SISTEMA
        
        assert funcionario.es_administrador() == False
        assert admin.es_administrador() == True


class TestFuncionarioFactoryMethods:
    """Tests para factory methods"""
    
    def test_crear_funcionario_basico(self):
        """Test factory method básico"""
        funcionario = Funcionario.crear_funcionario_basico("TEST001", "Test User")
        assert funcionario.id_funcionario == "TEST001"
        assert funcionario.cargo == CargoFuncionario.FUNCIONARIO
    
    def test_crear_desde_auth(self):
        """Test crear desde datos de AUTH"""
        datos_auth = {
            'user_id': 'JLOPEZ001',
            'full_name': 'José López García',
            'email': 'jose.lopez@test.com',
            'role': 'supervisor',
            'is_active': True
        }
        
        funcionario = Funcionario.crear_desde_auth(datos_auth)
        assert funcionario.id_funcionario == "JLOPEZ001"
        assert funcionario.cargo == CargoFuncionario.SUPERVISOR
        assert funcionario.email == "jose.lopez@test.com"
    
    def test_crear_si_valido_exitoso(self):
        """Test crear si válido exitoso"""
        funcionario = Funcionario.crear_si_valido("TEST001", "Test User", "funcionario")
        assert funcionario is not None
        assert funcionario.cargo == CargoFuncionario.FUNCIONARIO
    
    def test_crear_si_valido_fallido(self):
        """Test crear si válido fallido"""
        funcionario = Funcionario.crear_si_valido("TEST001", "Test User", "cargo_invalido")
        assert funcionario is None


class TestFuncionariosPredefinidos:
    """Tests para funcionarios predefinidos"""
    
    def test_obtener_todos(self):
        """Test obtener todos los funcionarios"""
        funcionarios = FuncionariosPredefinidos.obtener_todos()
        assert len(funcionarios) == 5
        ids = [f.id_funcionario for f in funcionarios]
        assert "LMURCIA001" in ids
        assert "ADMIN001" in ids
    
    def test_obtener_por_id(self):
        """Test buscar por ID"""
        funcionario = FuncionariosPredefinidos.obtener_por_id("LMURCIA001")
        assert funcionario is not None
        assert funcionario.nombre_completo == "Luis Fabian Murcia Salinas"
        
        no_existe = FuncionariosPredefinidos.obtener_por_id("NO_EXISTE")
        assert no_existe is None
    
    def test_obtener_por_cargo(self):
        """Test buscar por cargo"""
        supervisores = FuncionariosPredefinidos.obtener_por_cargo(CargoFuncionario.SUPERVISOR)
        assert len(supervisores) == 3
        ids = [s.id_funcionario for s in supervisores]
        assert "ARODRIGUEZ002" in ids
        assert "CLOPEZ003" in ids
    
    def test_obtener_supervisores_activos(self):
        """Test obtener supervisores activos"""
        supervisores = FuncionariosPredefinidos.obtener_supervisores_activos()
        assert len(supervisores) == 4  # ANA_RODRIGUEZ (supervisor), CARLOS_LOPEZ (supervisor), MARIA_GARCIA (admin), ADMIN_SISTEMA (admin)
        cargos = [s.cargo for s in supervisores]
        assert CargoFuncionario.FUNCIONARIO not in cargos