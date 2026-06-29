# services/retrieval-service/app/ingestion/hardware_detector.py
import shutil
import subprocess
import logging
import torch

logger = logging.getLogger("ingestion.hardware_detector")

def get_hardware_level() -> str:
    """
    Checks if a CUDA-enabled GPU is available.
    Returns 'LEVEL_2_GPU' if available, otherwise 'LEVEL_1_CPU'.
    """
    if torch.cuda.is_available():
        return "LEVEL_2_GPU"
    return "LEVEL_1_CPU"

def run_diagnostics() -> dict:
    """
    Verifies system dependencies for the OCR pipeline (Tesseract binary and language packs).
    If Tesseract or required packs are missing, lists warning recommendations instead of failing.
    """
    results = {
        "tesseract_installed": False,
        "eng_pack_available": False,
        "tam_pack_available": False,
        "ocr_ready": False,
        "warnings": []
    }
    
    # 1. Detect Tesseract Binary on System PATH
    tess_exe = shutil.which("tesseract")
    if tess_exe:
        results["tesseract_installed"] = True
        
        # 2. Check for English and Tamil Language Packs
        try:
            # Run tesseract list-langs. On some systems stderr contains warnings, we combine stdout/stderr.
            output = subprocess.check_output(
                ["tesseract", "--list-langs"], 
                stderr=subprocess.STDOUT
            ).decode("utf-8")
            
            # The first line is usually "List of available languages (X):"
            langs = [line.strip().lower() for line in output.splitlines() if line.strip()]
            
            if "eng" in langs:
                results["eng_pack_available"] = True
            if "tam" in langs:
                results["tam_pack_available"] = True
                
        except Exception as e:
            results["warnings"].append(f"Failed to query Tesseract language pack listing: {str(e)}")
    else:
        results["warnings"].append("Tesseract OCR binary was not found on the system PATH.")

    # Ingestion can run OCR fallback if Tamil (minimum for bilingual science) or English is configured.
    # To be fully operational, both are expected.
    results["ocr_ready"] = results["tesseract_installed"] and results["eng_pack_available"] and results["tam_pack_available"]
    
    return results

def log_ocr_status() -> None:
    """
    Prints diagnostic logs for OCR status to stdout/logger.
    """
    diag = run_diagnostics()
    hw_level = get_hardware_level()
    
    print("\n--- TamilEdu-SLM Ingestion Startup Diagnostics ---")
    print(f"Hardware Mode: {hw_level} ({'GPU Acceleration Enabled' if hw_level == 'LEVEL_2_GPU' else 'Running on CPU'})")
    
    print(f"{'[ OK ]' if diag['tesseract_installed'] else '[FAIL]'} Tesseract Installed")
    print(f"{'[ OK ]' if diag['eng_pack_available'] else '[FAIL]'} English Language Pack (eng)")
    print(f"{'[ OK ]' if diag['tam_pack_available'] else '[FAIL]'} Tamil Language Pack (tam)")
    
    if diag["ocr_ready"]:
        print("[ OK ] OCR Ready")
    else:
        print("[FAIL] OCR Ready (Fallback to direct text extraction only)")
        
    for warning in diag["warnings"]:
        print(f"[WARN] {warning}")
        
    if not diag["ocr_ready"]:
        print("\nSetup Instructions:")
        if not diag["tesseract_installed"]:
            print("  - Install Tesseract-OCR for your system (Windows: download installers, Linux: sudo apt install tesseract-ocr)")
        if not diag["eng_pack_available"] or not diag["tam_pack_available"]:
            print("  - Ensure 'eng.traineddata' and 'tam.traineddata' are placed in the Tesseract 'tessdata' folder.")
            print("  - Check that the TESSDATA_PREFIX environment variable is correctly configured.")
    print("---------------------------------------------------\n")
