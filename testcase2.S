0000000000400686 <main>:
  400686:	55                   	push   %rbp
  400687:	48 89 e5             	mov    %rsp,%rbp
  40068a:	c7 05 cc 09 20 00 00 	movl   $0x0,0x2009cc(%rip)        # 601060 <count>
  400691:	00 00 00 
  400694:	c7 05 d6 09 20 00 00 	movl   $0x0,0x2009d6(%rip)        # 601074 <flag>
  40069b:	00 00 00 
  40069e:	bf 28 09 40 00       	mov    $0x400928,%edi
  4006a3:	b8 00 00 00 00       	mov    $0x0,%eax
  4006a8:	e8 93 fe ff ff       	callq  400540 <printf@plt>
  4006ad:	be 68 10 60 00       	mov    $0x601068,%esi
  4006b2:	bf 49 09 40 00       	mov    $0x400949,%edi
  4006b7:	b8 00 00 00 00       	mov    $0x0,%eax
  4006bc:	e8 9f fe ff ff       	callq  400560 <__isoc99_scanf@plt>
  4006c1:	b8 00 00 00 00       	mov    $0x0,%eax
  4006c6:	e8 55 00 00 00       	callq  400720 <E>
  4006cb:	bf 68 10 60 00       	mov    $0x601068,%edi
  4006d0:	e8 5b fe ff ff       	callq  400530 <strlen@plt>
  4006d5:	48 89 c2             	mov    %rax,%rdx
  4006d8:	8b 05 82 09 20 00    	mov    0x200982(%rip),%eax        # 601060 <count>
  4006de:	48 98                	cltq   
  4006e0:	48 39 c2             	cmp    %rax,%rdx
  4006e3:	75 20                	jne    400705 <main+0x7f>
  4006e5:	8b 05 89 09 20 00    	mov    0x200989(%rip),%eax        # 601074 <flag>
  4006eb:	85 c0                	test   %eax,%eax
  4006ed:	75 16                	jne    400705 <main+0x7f>
  4006ef:	be 68 10 60 00       	mov    $0x601068,%esi
  4006f4:	bf 4c 09 40 00       	mov    $0x40094c,%edi
  4006f9:	b8 00 00 00 00       	mov    $0x0,%eax
  4006fe:	e8 3d fe ff ff       	callq  400540 <printf@plt>
  400703:	eb 14                	jmp    400719 <main+0x93>
  400705:	be 68 10 60 00       	mov    $0x601068,%esi
  40070a:	bf 70 09 40 00       	mov    $0x400970,%edi
  40070f:	b8 00 00 00 00       	mov    $0x0,%eax
  400714:	e8 27 fe ff ff       	callq  400540 <printf@plt>
  400719:	b8 00 00 00 00       	mov    $0x0,%eax
  40071e:	5d                   	pop    %rbp
  40071f:	c3                   	retq   

0000000000400720 <E>:
  400720:	55                   	push   %rbp
  400721:	48 89 e5             	mov    %rsp,%rbp
  400724:	b8 00 00 00 00       	mov    $0x0,%eax
  400729:	e8 0d 00 00 00       	callq  40073b <T>
  40072e:	b8 00 00 00 00       	mov    $0x0,%eax
  400733:	e8 28 01 00 00       	callq  400860 <Eprime>
  400738:	90                   	nop
  400739:	5d                   	pop    %rbp
  40073a:	c3                   	retq   

000000000040073b <T>:
  40073b:	55                   	push   %rbp
  40073c:	48 89 e5             	mov    %rsp,%rbp
  40073f:	48 83 ec 10          	sub    $0x10,%rsp
  400743:	b8 00 00 00 00       	mov    $0x0,%eax
  400748:	e8 67 00 00 00       	callq  4007b4 <check>
  40074d:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  400754:	eb 0e                	jmp    400764 <T+0x29>
  400756:	bf 8f 09 40 00       	mov    $0x40098f,%edi
  40075b:	e8 c0 fd ff ff       	callq  400520 <puts@plt>
  400760:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  400764:	83 7d fc 09          	cmpl   $0x9,-0x4(%rbp)
  400768:	7e ec                	jle    400756 <T+0x1b>
  40076a:	b8 00 00 00 00       	mov    $0x0,%eax
  40076f:	e8 03 00 00 00       	callq  400777 <Tprime>
  400774:	90                   	nop
  400775:	c9                   	leaveq 
  400776:	c3                   	retq   

0000000000400777 <Tprime>:
  400777:	55                   	push   %rbp
  400778:	48 89 e5             	mov    %rsp,%rbp
  40077b:	8b 05 df 08 20 00    	mov    0x2008df(%rip),%eax        # 601060 <count>
  400781:	48 98                	cltq   
  400783:	0f b6 80 68 10 60 00 	movzbl 0x601068(%rax),%eax
  40078a:	3c 2a                	cmp    $0x2a,%al
  40078c:	75 23                	jne    4007b1 <Tprime+0x3a>
  40078e:	8b 05 cc 08 20 00    	mov    0x2008cc(%rip),%eax        # 601060 <count>
  400794:	83 c0 01             	add    $0x1,%eax
  400797:	89 05 c3 08 20 00    	mov    %eax,0x2008c3(%rip)        # 601060 <count>
  40079d:	b8 00 00 00 00       	mov    $0x0,%eax
  4007a2:	e8 0d 00 00 00       	callq  4007b4 <check>
  4007a7:	b8 00 00 00 00       	mov    $0x0,%eax
  4007ac:	e8 c6 ff ff ff       	callq  400777 <Tprime>
  4007b1:	90                   	nop
  4007b2:	5d                   	pop    %rbp
  4007b3:	c3                   	retq   

00000000004007b4 <check>:
  4007b4:	55                   	push   %rbp
  4007b5:	48 89 e5             	mov    %rsp,%rbp
  4007b8:	e8 b3 fd ff ff       	callq  400570 <__ctype_b_loc@plt>
  4007bd:	48 8b 10             	mov    (%rax),%rdx
  4007c0:	8b 05 9a 08 20 00    	mov    0x20089a(%rip),%eax        # 601060 <count>
  4007c6:	48 98                	cltq   
  4007c8:	0f b6 80 68 10 60 00 	movzbl 0x601068(%rax),%eax
  4007cf:	48 0f be c0          	movsbq %al,%rax
  4007d3:	48 01 c0             	add    %rax,%rax
  4007d6:	48 01 d0             	add    %rdx,%rax
  4007d9:	0f b7 00             	movzwl (%rax),%eax
  4007dc:	0f b7 c0             	movzwl %ax,%eax
  4007df:	83 e0 08             	and    $0x8,%eax
  4007e2:	85 c0                	test   %eax,%eax
  4007e4:	74 11                	je     4007f7 <check+0x43>
  4007e6:	8b 05 74 08 20 00    	mov    0x200874(%rip),%eax        # 601060 <count>
  4007ec:	83 c0 01             	add    $0x1,%eax
  4007ef:	89 05 6b 08 20 00    	mov    %eax,0x20086b(%rip)        # 601060 <count>
  4007f5:	eb 66                	jmp    40085d <check+0xa9>
  4007f7:	8b 05 63 08 20 00    	mov    0x200863(%rip),%eax        # 601060 <count>
  4007fd:	48 98                	cltq   
  4007ff:	0f b6 80 68 10 60 00 	movzbl 0x601068(%rax),%eax
  400806:	3c 28                	cmp    $0x28,%al
  400808:	75 49                	jne    400853 <check+0x9f>
  40080a:	8b 05 50 08 20 00    	mov    0x200850(%rip),%eax        # 601060 <count>
  400810:	83 c0 01             	add    $0x1,%eax
  400813:	89 05 47 08 20 00    	mov    %eax,0x200847(%rip)        # 601060 <count>
  400819:	b8 00 00 00 00       	mov    $0x0,%eax
  40081e:	e8 fd fe ff ff       	callq  400720 <E>
  400823:	8b 05 37 08 20 00    	mov    0x200837(%rip),%eax        # 601060 <count>
  400829:	48 98                	cltq   
  40082b:	0f b6 80 68 10 60 00 	movzbl 0x601068(%rax),%eax
  400832:	3c 29                	cmp    $0x29,%al
  400834:	75 11                	jne    400847 <check+0x93>
  400836:	8b 05 24 08 20 00    	mov    0x200824(%rip),%eax        # 601060 <count>
  40083c:	83 c0 01             	add    $0x1,%eax
  40083f:	89 05 1b 08 20 00    	mov    %eax,0x20081b(%rip)        # 601060 <count>
  400845:	eb 16                	jmp    40085d <check+0xa9>
  400847:	c7 05 23 08 20 00 01 	movl   $0x1,0x200823(%rip)        # 601074 <flag>
  40084e:	00 00 00 
  400851:	eb 0a                	jmp    40085d <check+0xa9>
  400853:	c7 05 17 08 20 00 01 	movl   $0x1,0x200817(%rip)        # 601074 <flag>
  40085a:	00 00 00 
  40085d:	90                   	nop
  40085e:	5d                   	pop    %rbp
  40085f:	c3                   	retq   

0000000000400860 <Eprime>:
  400860:	55                   	push   %rbp
  400861:	48 89 e5             	mov    %rsp,%rbp
  400864:	8b 05 f6 07 20 00    	mov    0x2007f6(%rip),%eax        # 601060 <count>
  40086a:	48 98                	cltq   
  40086c:	0f b6 80 68 10 60 00 	movzbl 0x601068(%rax),%eax
  400873:	3c 2b                	cmp    $0x2b,%al
  400875:	75 23                	jne    40089a <Eprime+0x3a>
  400877:	8b 05 e3 07 20 00    	mov    0x2007e3(%rip),%eax        # 601060 <count>
  40087d:	83 c0 01             	add    $0x1,%eax
  400880:	89 05 da 07 20 00    	mov    %eax,0x2007da(%rip)        # 601060 <count>
  400886:	b8 00 00 00 00       	mov    $0x0,%eax
  40088b:	e8 ab fe ff ff       	callq  40073b <T>
  400890:	b8 00 00 00 00       	mov    $0x0,%eax
  400895:	e8 c6 ff ff ff       	callq  400860 <Eprime>
  40089a:	90                   	nop
  40089b:	5d                   	pop    %rbp
  40089c:	c3                   	retq   
  40089d:	0f 1f 00             	nopl   (%rax)

