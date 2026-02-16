import { useState } from 'react';
import { createUser } from '../services/api';
import { useQueryClient } from '@tanstack/react-query';

interface CreateUserFormProps {
    onSuccess: (newUserId: number) => void;
    onCancel: () => void;
}

const CreateUserForm = ({ onSuccess, onCancel }: CreateUserFormProps) => {
    const [formData, setFormData] = useState({
        nombre: '',
        password: '',
        edad: '',
        genero: 'Masculino'
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const queryClient = useQueryClient();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            // Validate
            if (!formData.nombre || !formData.password || !formData.edad) {
                throw new Error('Por favor complete todos los campos requeridos');
            }

            const payload = {
                ...formData,
                edad: parseInt(formData.edad)
            };

            const res = await createUser(payload);

            // Invalidate users query to refresh list
            queryClient.invalidateQueries({ queryKey: ['users'] });

            if (res.data && res.data.user) {
                onSuccess(res.data.user.id);
            } else {
                onSuccess(0); // Fallback if no ID returned
            }
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.error || err.message || 'Error al crear usuario');
        } finally {
            setIsLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const inputStyle = {
        width: '100%',
        padding: '12px',
        borderRadius: '8px',
        border: '1px solid #444',
        background: '#2c2e33',
        color: '#fff',
        fontSize: '16px',
        marginBottom: '20px',
        outline: 'none'
    };

    const labelStyle = {
        display: 'block',
        marginBottom: '8px',
        color: '#aaa',
        fontSize: '0.9em'
    };

    return (
        <div style={{
            background: '#151722',
            padding: '40px',
            borderRadius: '16px',
            maxWidth: '600px',
            margin: '0 auto',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            border: '1px solid #2c2e33'
        }}>
            <h2 style={{
                color: '#fff',
                marginBottom: '30px',
                textAlign: 'center',
                borderBottom: '1px solid #2c2e33',
                paddingBottom: '20px'
            }}>
                👤 Registrar Nuevo Usuario
            </h2>

            {error && (
                <div style={{
                    background: 'rgba(255, 107, 107, 0.1)',
                    border: '1px solid #ff6b6b',
                    color: '#ff6b6b',
                    padding: '15px',
                    borderRadius: '8px',
                    marginBottom: '20px',
                    textAlign: 'center'
                }}>
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit}>
                <div>
                    <label style={labelStyle}>Nombre Completo *</label>
                    <input
                        type="text"
                        name="nombre"
                        value={formData.nombre}
                        onChange={handleChange}
                        style={inputStyle}
                        placeholder="Ej. Juan Pérez"
                        autoFocus
                    />
                </div>

                <div>
                    <label style={labelStyle}>Contraseña *</label>
                    <input
                        type="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        style={inputStyle}
                        placeholder="••••••"
                    />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                    <div>
                        <label style={labelStyle}>Edad *</label>
                        <input
                            type="number"
                            name="edad"
                            value={formData.edad}
                            onChange={handleChange}
                            style={inputStyle}
                            placeholder="Ej. 75"
                            min="1"
                            max="120"
                        />
                    </div>
                    <div>
                        <label style={labelStyle}>Género</label>
                        <select
                            name="genero"
                            value={formData.genero}
                            onChange={handleChange}
                            style={inputStyle}
                        >
                            <option value="Masculino">Masculino</option>
                            <option value="Femenino">Femenino</option>
                            <option value="Otro">Otro</option>
                        </select>
                    </div>
                </div>

                <div style={{ display: 'flex', gap: '15px', marginTop: '20px' }}>
                    <button
                        type="button"
                        onClick={onCancel}
                        style={{
                            flex: 1,
                            padding: '15px',
                            borderRadius: '8px',
                            border: '1px solid #444',
                            background: 'transparent',
                            color: '#aaa',
                            cursor: 'pointer',
                            fontSize: '16px',
                            fontWeight: 'bold',
                            transition: 'all 0.2s'
                        }}
                    >
                        Cancelar
                    </button>
                    <button
                        type="submit"
                        disabled={isLoading}
                        style={{
                            flex: 1,
                            padding: '15px',
                            borderRadius: '8px',
                            border: 'none',
                            background: isLoading ? '#2c2e33' : '#51cf66',
                            color: isLoading ? '#888' : '#fff',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            fontSize: '16px',
                            fontWeight: 'bold',
                            boxShadow: isLoading ? 'none' : '0 4px 15px rgba(81, 207, 102, 0.3)',
                            transition: 'all 0.2s'
                        }}
                    >
                        {isLoading ? 'Registrando...' : 'Registrar Usuario'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default CreateUserForm;
