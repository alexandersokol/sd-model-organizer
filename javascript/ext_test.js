function doTheAddClick(){
    const btn = gradioApp().getElementById('do_the_add_button')
    if (btn) btn.click()
}

function onHidden() { // stop refresh interval when tab is not visible
    console.log("onHidden")
  }
  
  function onVisible() { // start refresh interval tab is when visible
    console.log("onVisible")
  }
  
  function initLoading() { // triggered on gradio change to monitor when ui gets sufficiently constructed
    if (loaded) return
    const block = gradioApp().getElementById('test_interface');
    if (!block) return
    intersectionObserver = new IntersectionObserver((entries) => {
      if (entries[0].intersectionRatio <= 0) onHidden();
      if (entries[0].intersectionRatio > 0) onVisible();
    });
    intersectionObserver.observe(block); // monitor visibility of tab
  }
  
  function initInitial() { // just setup monitor for gradio events
    const mutationObserver = new MutationObserver(initLoading)
    mutationObserver.observe(gradioApp(), { childList: true, subtree: true }); // monitor changes to gradio
  }
  
  document.addEventListener('DOMContentLoaded', initInitial);