from controllers.default_controller import DefaultController
from controllers.data_controller import DataController
from helpers.wrappers import Wrappers

def initialize_routes(app, default_controller, data_controller):
    # Health Check Route
    app.add_url_rule("/api/health", 
                     view_func=default_controller.health_check,
                     methods=['GET'])

    # Get Count Route
    app.add_url_rule("/api/get_count", 
                     view_func=Wrappers.require_api_key(data_controller.get_count),
                     methods=['GET'])

    # Vectorize Database Records Route
    app.add_url_rule("/api/vectorize_database_records_for_lu_type_table", 
                     view_func=Wrappers.require_api_key(data_controller.vectorize_database_records_for_lu_type_table),
                     methods=['POST'])
    
    app.add_url_rule("/api/insert_lu_type_table_and_vectorize_into_database", 
                    view_func=Wrappers.require_api_key(data_controller.insert_lu_type_table_and_vectorize_into_database),
                    methods=['POST'])
    
    app.add_url_rule("/api/insert_exercise_and_vectorize_into_database", 
                view_func=Wrappers.require_api_key(data_controller.insert_exercise_and_vectorize_into_database),
                methods=['POST'])
    
    app.add_url_rule("/api/insert_emotion_cnn_ai_training", 
            view_func=Wrappers.require_api_key(data_controller.insert_emotion_cnn_ai_training),
            methods=['POST'])
    
    app.add_url_rule("/api/insert_rl_training_info", 
        view_func=Wrappers.require_api_key(data_controller.insert_rl_training_info),
        methods=['POST'])

    app.add_url_rule("/api/insert_encoding_model_training", 
        view_func=Wrappers.require_api_key(data_controller.insert_encoding_model_training),
        methods=['POST'])

    # Route for inserting emotion CNN AI training data
    app.add_url_rule(
        "/api/insert_emotion_cnn_ai_training", 
        view_func=Wrappers.require_api_key(data_controller.insert_emotion_cnn_ai_training), 
        methods=['POST']
    )

    # Route for inserting encoding model training data
    app.add_url_rule(
        "/api/insert_encoding_model_training", 
        view_func=Wrappers.require_api_key(data_controller.insert_encoding_model_training), 
        methods=['POST']
    )

    # Route for getting feedback by user ID
    app.add_url_rule(
        "/api/get_feedback_by_user/<int:user_id>", 
        view_func=Wrappers.require_api_key(data_controller.get_feedback_by_user), 
        methods=['GET']
    )

    # Route for getting feedback rating options
    app.add_url_rule(
        "/api/get_feedback_rating_options", 
        view_func=Wrappers.require_api_key(data_controller.get_feedback_rating_options), 
        methods=['GET']
    )

    # Route for getting RL training info
    app.add_url_rule(
        "/api/get_rl_training_info", 
        view_func=Wrappers.require_api_key(data_controller.get_rl_training_info), 
        methods=['GET']
    )

    # Route for inserting RL training info
    app.add_url_rule(
        "/api/insert_rl_training_info", 
        view_func=Wrappers.require_api_key(data_controller.insert_rl_training_info), 
        methods=['POST']
    )





