let agree = document.querySelector('.agree')
let disagree = document.querySelector('.disagree')

function approve(approval) {
  axios({
    method: 'post',
    url: '/publish/approve',
    data: {
      is_permitted: approval,
      check_opinion: '无',
      event_id: parseInt(location.href.split('=')[1]),
      student_id: document.querySelector('.user_form .stu_id input').value
    }
  })
    .then(result => {
      console.log(result)
      popupTop.innerHTML = '审批成功！'
      popup.classList.remove('hide')
    })
    .catch(error => {
      console.dir(error)
    })
}

agree.addEventListener('click', () => {
  approve(1)
})

disagree.addEventListener('click', () => {
  approve(-1)
})
