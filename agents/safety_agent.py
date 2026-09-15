from ultralytics import YOLO


class SafetyAgent:

    VIOLATION_CLASSES = {
        "NO-Hardhat",
        "NO-Mask",
        "NO-Safety Vest",
    }

    def __init__(self):
        self.model = YOLO(
            "runs/detect/models/safety_yolo-2/weights/best.pt"
        )

    # ========================================================
    # IMAGE-BASED INSPECTION
    # ========================================================

    def inspect_image(self, image_path):

        results = self.model(
            image_path,
            verbose=False
        )

        return self._process_results(results)

    # ========================================================
    # REAL-TIME FRAME INSPECTION
    # ========================================================

    def inspect_frame(self, frame):

        results = self.model(
            frame,
            verbose=False,
            conf=0.50,
            imgsz=640
        )

        return self._process_results(results)

    # ========================================================
    # PROCESS YOLO RESULTS
    # ========================================================

    def _process_results(self, results):

        detections = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(box.cls[0])

                confidence = float(box.conf[0])

                label = result.names[class_id]

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                detections.append({
                    "label": label,
                    "confidence": round(
                        confidence,
                        2
                    ),
                    "box": (
                        x1,
                        y1,
                        x2,
                        y2
                    )
                })

        # ----------------------------------------------------
        # PPE violations
        # ----------------------------------------------------

        violations = [
            item
            for item in detections
            if item["label"] in self.VIOLATION_CLASSES
        ]

        # ----------------------------------------------------
        # Workers
        # ----------------------------------------------------

        workers_detected = sum(
            1
            for item in detections
            if item["label"] == "Person"
        )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        status = (
            "Unsafe"
            if violations
            else "Safe"
        )

        return {
            "status": status,

            "detections": detections,

            "violations": violations,

            "workers_detected": workers_detected,

            "violation_count": len(violations)
        }