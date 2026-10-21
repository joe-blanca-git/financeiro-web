from sqlalchemy.orm import Session
from app.models.cliente import Cliente
from app.models.representante import Representante

class ClienteService:
    @staticmethod
    def get_clientes(db: Session, id_representante: int = None):
        clientes = (
            db.query(Cliente, Representante.nome.label("representante_nome"))
            .outerjoin(Representante, Representante.idRepresentante == Cliente.idRepresentante)
            .order_by(Cliente.nome.asc())
            .all()
        )

        # linked: o cliente é do representante informado. representanteNome: dono atual
        # (cada cliente tem um único representante, em clientes.idRepresentante).
        return [
            {
                "idclientes": c.idclientes,
                "codigo": c.codigo,
                "nome": c.nome,
                "linked": bool(id_representante) and c.idRepresentante == id_representante,
                "representanteNome": representante_nome,
            }
            for c, representante_nome in clientes
        ]

    @staticmethod
    def vincular_clientes(db: Session, id_representante: int, ids_clientes: list[int]):
        # Desmarcados: deixam de ter representante
        db.query(Cliente).filter(
            Cliente.idRepresentante == id_representante,
            ~Cliente.idclientes.in_(ids_clientes or [0]),
        ).update({Cliente.idRepresentante: None}, synchronize_session=False)

        # Marcados: passam a ser deste representante (inclusive se eram de outro)
        if ids_clientes:
            db.query(Cliente).filter(Cliente.idclientes.in_(ids_clientes)).update(
                {Cliente.idRepresentante: id_representante}, synchronize_session=False
            )

        db.commit()
        return True
