from natacha_base.observer import run_learning_cycle


def create_app():

    @app.route("/ops/force_learn", methods=["POST"])
    def force_learn():
        """
        Forzar un ciclo de aprendizaje manualmente.
        Lee las lecciones de Firestore y devuelve un resumen.
        """
        try:
            result = run_learning_cycle()
            return jsonify({"status": "ok", "forced": True, "result": result}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return app
