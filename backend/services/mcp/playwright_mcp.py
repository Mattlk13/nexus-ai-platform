"""
Real Playwright MCP Implementation for NEXUS
Direct Playwright integration without Docker
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import base64
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class PlaywrightMCPServer:
    """
    Real Playwright MCP Server using direct Playwright installation
    Provides browser automation capabilities without Docker
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.initialized = False
        logger.info("Playwright MCP Server created")
    
    async def initialize(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            self.page = await self.context.new_page()
            self.initialized = True
            logger.info("✅ Playwright browser initialized (Chromium)")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {e}")
            return False
    
    async def goto(self, url: str, timeout: int = 30000) -> Dict[str, Any]:
        """Navigate to URL"""
        try:
            if not self.initialized:
                await self.initialize()
            
            response = await self.page.goto(url, timeout=timeout, wait_until='networkidle')
            
            return {
                "success": True,
                "tool": "browser_goto",
                "url": url,
                "status": response.status if response else None,
                "title": await self.page.title(),
                "mode": "REAL_PLAYWRIGHT"
            }
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {
                "success": False,
                "tool": "browser_goto",
                "error": str(e)
            }
    
    async def screenshot(self, full_page: bool = False) -> Dict[str, Any]:
        """Take screenshot of current page"""
        try:
            if not self.initialized or not self.page:
                return {"success": False, "error": "Browser not initialized"}
            
            screenshot_bytes = await self.page.screenshot(
                full_page=full_page,
                type='png'
            )
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            return {
                "success": True,
                "tool": "browser_screenshot",
                "screenshot": screenshot_base64,
                "size_bytes": len(screenshot_bytes),
                "format": "png",
                "full_page": full_page,
                "mode": "REAL_PLAYWRIGHT"
            }
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return {
                "success": False,
                "tool": "browser_screenshot",
                "error": str(e)
            }
    
    async def click(self, selector: str, timeout: int = 30000) -> Dict[str, Any]:
        """Click an element"""
        try:
            if not self.initialized or not self.page:
                return {"success": False, "error": "Browser not initialized"}
            
            await self.page.click(selector, timeout=timeout)
            
            return {
                "success": True,
                "tool": "browser_click",
                "selector": selector,
                "mode": "REAL_PLAYWRIGHT"
            }
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {
                "success": False,
                "tool": "browser_click",
                "error": str(e),
                "selector": selector
            }
    
    async def fill(self, selector: str, text: str, timeout: int = 30000) -> Dict[str, Any]:
        """Fill a form field"""
        try:
            if not self.initialized or not self.page:
                return {"success": False, "error": "Browser not initialized"}
            
            await self.page.fill(selector, text, timeout=timeout)
            
            return {
                "success": True,
                "tool": "browser_fill",
                "selector": selector,
                "text_length": len(text),
                "mode": "REAL_PLAYWRIGHT"
            }
        except Exception as e:
            logger.error(f"Fill failed: {e}")
            return {
                "success": False,
                "tool": "browser_fill",
                "error": str(e),
                "selector": selector
            }
    
    async def evaluate(self, script: str) -> Dict[str, Any]:
        """Execute JavaScript on page"""
        try:
            if not self.initialized or not self.page:
                return {"success": False, "error": "Browser not initialized"}
            
            result = await self.page.evaluate(script)
            
            return {
                "success": True,
                "tool": "browser_evaluate",
                "result": result,
                "mode": "REAL_PLAYWRIGHT"
            }
        except Exception as e:
            logger.error(f"Evaluate failed: {e}")
            return {
                "success": False,
                "tool": "browser_evaluate",
                "error": str(e)
            }
    
    async def get_content(self) -> Dict[str, Any]:
        """Get page HTML content"""
        try:
            if not self.initialized or not self.page:
                return {"success": False, "error": "Browser not initialized"}
            
            content = await self.page.content()
            
            return {
                "success": True,
                "tool": "browser_get_content",
                "content": content,
                "length": len(content),
                "mode": "REAL_PLAYWRIGHT"
            }
        except Exception as e:
            logger.error(f"Get content failed: {e}")
            return {
                "success": False,
                "tool": "browser_get_content",
                "error": str(e)
            }
    
    async def pdf(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Generate PDF of current page"""
        try:
            if not self.initialized or not self.page:
                return {"success": False, "error": "Browser not initialized"}
            
            if path:
                await self.page.pdf(path=path)
                return {
                    "success": True,
                    "tool": "browser_pdf",
                    "path": path,
                    "mode": "REAL_PLAYWRIGHT"
                }
            else:
                pdf_bytes = await self.page.pdf()
                pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
                return {
                    "success": True,
                    "tool": "browser_pdf",
                    "pdf": pdf_base64,
                    "size_bytes": len(pdf_bytes),
                    "mode": "REAL_PLAYWRIGHT"
                }
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return {
                "success": False,
                "tool": "browser_pdf",
                "error": str(e)
            }
    
    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> Dict[str, Any]:
        """Wait for element to appear"""
        try:
            if not self.initialized or not self.page:
                return {"success": False, "error": "Browser not initialized"}
            
            await self.page.wait_for_selector(selector, timeout=timeout)
            
            return {
                "success": True,
                "tool": "browser_wait_for_selector",
                "selector": selector,
                "mode": "REAL_PLAYWRIGHT"
            }
        except Exception as e:
            logger.error(f"Wait for selector failed: {e}")
            return {
                "success": False,
                "tool": "browser_wait_for_selector",
                "error": str(e),
                "selector": selector
            }
    
    async def get_text(self, selector: str) -> Dict[str, Any]:
        """Get text content of an element"""
        try:
            if not self.initialized or not self.page:
                return {"success": False, "error": "Browser not initialized"}
            
            text = await self.page.text_content(selector)
            
            return {
                "success": True,
                "tool": "browser_get_text",
                "selector": selector,
                "text": text,
                "mode": "REAL_PLAYWRIGHT"
            }
        except Exception as e:
            logger.error(f"Get text failed: {e}")
            return {
                "success": False,
                "tool": "browser_get_text",
                "error": str(e),
                "selector": selector
            }
    
    async def cleanup(self):
        """Clean up Playwright resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.initialized = False
            logger.info("Playwright cleaned up")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Singleton instance
_playwright_instance: Optional[PlaywrightMCPServer] = None

def get_playwright_server() -> PlaywrightMCPServer:
    """Get or create Playwright server singleton"""
    global _playwright_instance
    if _playwright_instance is None:
        _playwright_instance = PlaywrightMCPServer(headless=True)
    return _playwright_instance
