/**
 * Browser Extension Cleanup Script
 *
 * This script aggressively removes browser extension attributes that cause
 * React hydration errors. It runs immediately when loaded and sets up
 * observers to handle dynamic attribute injection.
 *
 * Common extensions that inject attributes:
 * - BitDefender (bis_skin_checked, bis_register)
 * - AdBlock extensions (data-adblock-*)
 * - Password managers (data-extension-*)
 * - Security extensions (__processed_*)
 */

(function() {
  'use strict';

  // List of extension attributes that cause hydration issues
  const EXTENSION_ATTRIBUTES = [
    'bis_skin_checked',
    'bis_register',
    '__processed_3156a7e1-e5c3-47de-ae90-2e1521714a72__',
    'data-adblock-key',
    'data-extension-id',
    'data-security-key',
    'data-lastpass-icon-added',
    'data-1p-ignore',
    'data-bitwarden-watching',
    'grammarly-extension',
    '__processed__',
    'bis_id',
    'bis_size'
  ];

  // Clean up extension attributes from elements
  function cleanupAttributes(element = document) {
    EXTENSION_ATTRIBUTES.forEach(attr => {
      const elements = element.querySelectorAll(`[${attr}]`);
      elements.forEach(el => {
        try {
          el.removeAttribute(attr);
        } catch (e) {
          // Ignore errors for read-only attributes
        }
      });
    });
  }

  // Clean up extension-injected text nodes and comments
  function cleanupNodes(element = document) {
    const walker = document.createTreeWalker(
      element,
      NodeFilter.SHOW_COMMENT,
      null,
      false
    );

    const comments = [];
    let node;
    while (node = walker.nextNode()) {
      // Remove extension-injected comments
      if (node.nodeValue && (
        node.nodeValue.includes('BitDefender') ||
        node.nodeValue.includes('extension') ||
        node.nodeValue.includes('adblock')
      )) {
        comments.push(node);
      }
    }

    comments.forEach(comment => {
      try {
        comment.remove();
      } catch (e) {
        // Ignore removal errors
      }
    });
  }

  // Immediate cleanup
  function immediateCleanup() {
    cleanupAttributes();
    cleanupNodes();
  }

  // Set up mutation observer to handle dynamic injections
  function setupObserver() {
    if (!window.MutationObserver) return;

    const observer = new MutationObserver(mutations => {
      let needsCleanup = false;

      mutations.forEach(mutation => {
        // Check for attribute changes
        if (mutation.type === 'attributes') {
          const attrName = mutation.attributeName;
          if (EXTENSION_ATTRIBUTES.includes(attrName)) {
            mutation.target.removeAttribute(attrName);
          }
        }
        // Check for added nodes
        else if (mutation.type === 'childList') {
          mutation.addedNodes.forEach(node => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              // Check if the added element has extension attributes
              const hasExtensionAttrs = EXTENSION_ATTRIBUTES.some(attr =>
                node.hasAttribute && node.hasAttribute(attr)
              );
              if (hasExtensionAttrs) {
                needsCleanup = true;
              }
            }
          });
        }
      });

      if (needsCleanup) {
        // Debounce cleanup to avoid excessive calls
        clearTimeout(window.__extensionCleanupTimeout);
        window.__extensionCleanupTimeout = setTimeout(immediateCleanup, 10);
      }
    });

    // Observe the entire document
    observer.observe(document, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: EXTENSION_ATTRIBUTES
    });

    // Store observer reference for potential cleanup
    window.__extensionObserver = observer;
  }

  // Override setAttribute to prevent extension attribute injection
  function preventAttributeInjection() {
    const originalSetAttribute = Element.prototype.setAttribute;

    Element.prototype.setAttribute = function(name, value) {
      if (EXTENSION_ATTRIBUTES.includes(name)) {
        // Silently ignore extension attribute attempts
        return;
      }
      return originalSetAttribute.call(this, name, value);
    };
  }

  // Run cleanup immediately if DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      immediateCleanup();
      setupObserver();
      preventAttributeInjection();

      // Additional cleanup after a short delay for late injections
      setTimeout(immediateCleanup, 100);
      setTimeout(immediateCleanup, 500);
    });
  } else {
    immediateCleanup();
    setupObserver();
    preventAttributeInjection();

    // Cleanup for already-injected content
    setTimeout(immediateCleanup, 0);
    setTimeout(immediateCleanup, 10);
    setTimeout(immediateCleanup, 100);
  }

  // Cleanup before React hydration (Next.js specific)
  if (typeof window !== 'undefined') {
    const originalConsoleError = console.error;
    console.error = function(...args) {
      const message = args[0] || '';

      // Suppress hydration errors related to extension attributes
      if (typeof message === 'string' && (
        message.includes('hydrat') && (
          message.includes('bis_skin_checked') ||
          message.includes('bis_register') ||
          message.includes('__processed_')
        )
      )) {
        // Run immediate cleanup and suppress the error
        immediateCleanup();
        return;
      }

      // Allow other errors through
      return originalConsoleError.apply(console, args);
    };
  }

  // Export cleanup functions for manual use
  window.__extensionCleanup = {
    cleanup: immediateCleanup,
    attributes: EXTENSION_ATTRIBUTES,
    observer: null
  };

  // Run final cleanup before page unload
  window.addEventListener('beforeunload', function() {
    if (window.__extensionObserver) {
      window.__extensionObserver.disconnect();
    }
  });

})();
