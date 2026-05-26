export const evidence = {
  loraError: `RuntimeError: Failed to load LoRA adapter ticket-triage:
'base_model.model.model.language_model.layers.15.self_attn.v_proj.lora_A.weight'`,

  flashinferWarning: `Bidirectional attention for image tokens requires TritonAttnBackend.
Falling back to causal attention, which may degrade image quality.`,

  flashinferError: `FlashInfer Internal Error: Invalid configuration :
NUM_MMA_Q=1 NUM_MMA_D_QK=32 NUM_MMA_D_VO=32 NUM_MMA_KV=1
NUM_WARPS_Q=4 NUM_WARPS_KV=1`,

  // The PEFT-generated key shape that SGLang's loader could not place.
  adapterKeyShape: `base_model.model.model.language_model.layers.<N>.self_attn.{q,k,v,o}_proj.lora_{A,B}.weight`,

  // The client-side symptom of crime #2.
  clientDisconnect: `http.client.RemoteDisconnected: Remote end closed connection without response`
};
