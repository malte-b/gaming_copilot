import { MessageCircleIcon } from "lucide-react";

export default function Bubble() {
  return (
    <div
      className="bubble"
      style={{
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        width: "100px",
        height: "100px",
        borderRadius: "50%",
        backgroundColor: "#3498db",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        cursor: "pointer",
      }}
    >
      <MessageCircleIcon color="white" size={40} />
    </div>
  );
}
