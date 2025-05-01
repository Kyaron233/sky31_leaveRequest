// 事件委托：绑定底部导航栏点击事件
let bottomNav = document.querySelector('.bottom_nav')
bottomNav.addEventListener('click', e => {
  let department = localStorage.getItem('department')
  let clickedEle = e.target.closest('li')
  if (clickedEle) {
    let pageId = clickedEle.id
    // 对行政人事部做特殊处理
    if (pageId === 'history' && department === 'HR') {
      location.href = '../page/AP_history.html'
      return
    } else {
      location.href = `../page/${pageId}.html`
    }
  }
})
