def _get_player_name_case():
    return """
        CASE player.id
            WHEN 4354 THEN 'Philip Foden'
            WHEN 25742 THEN 'Karly Roestbakken'
            WHEN 25546 THEN 'Cheyna Lee Matthews'
            WHEN 4951 THEN 'Quinn'
            WHEN 5082 THEN 'Marta Vieira da Silva'
            WHEN 18617 THEN 'Mykola Matviyenko'
            WHEN 3961 THEN 'N''Golo Kanté'
            WHEN 5659 THEN 'Khadim N''Diaye'
            WHEN 401453 THEN 'David Ngog'
            WHEN 184468 THEN 'Álvaro Zamora'
            ELSE player.name
        END
    """
