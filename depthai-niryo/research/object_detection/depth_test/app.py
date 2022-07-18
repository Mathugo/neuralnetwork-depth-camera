from object_detection import ObjectDetection


od = ObjectDetection()
od.configure_pipeline()
od.configure_properties()
od.configure_link()
od.run()
