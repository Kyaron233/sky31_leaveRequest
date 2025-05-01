// 事件委托：删除成员信息
let memberItems = document.querySelector('.member_items')
memberItems.addEventListener('click', e => {
  let target = e.target
  if (target.classList.contains('delete')) {
    // 获取要删除的对象
    deleteEle = target.parentElement
    // 弹窗提示：确认删除
    // 对弹窗内容做一些操作
    popupTop.innerHTML = '确认删除该成员'
    // 取消“确定”按钮直接关闭弹窗的功能
    popupBottom.querySelector('.close').classList.remove('close')
    popupBottom.innerHTML = '<button class="determine delete">确定</button><button class="cancle close">取消</button>'
    popup.classList.remove('hide')
  }
})

// 定义函数，执行删除操作
function deleteMember(deleteEle) {
  // 发送请求删除该成员
  let deleteId = deleteEle.querySelector('#stu_id').innerHTML
  axios({
    method: 'post',
    url: '/delete',
    data: {
      student_id: deleteId
    }
  })
    .then(result => {
      // 删除页面上的对应元素
      memberItems.removeChild(deleteEle)
      // 删除成功弹窗
      popupTop.innerHTML = '删除成功！'
      popup.classList.remove('hide')
      // 修改缓存内容
      localStorage.setItem('memberItems', memberItems.outerHTML)
      // 刷新当前页面
      document.querySelector('.message_content').innerHTML = localStorage.getItem('memberItems')
    })
    .catch(error => {
      console.dir(error)
      popupTop.innerHTML = '删除失败！'
      popup.classList.remove('hide')
    })
}
